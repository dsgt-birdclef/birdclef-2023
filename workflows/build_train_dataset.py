"""
Module to build the embedding training dataset from the audio files.

We do a number of things here:

- Pad each audio file to be an increment of 3 seconds, with some noise added
- Sound separate the audio files
- Extract embeddings and predictions from the birdnet model on the resulting track
- Consolidate a single parquet dataset with embeddings and predictions

We perform this on a per-track basis.
"""

import itertools
import json
import os
from pathlib import Path

import librosa
import luigi
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import soundfile as sf
import tqdm
from pyspark.sql import Row

from birdclef import birdnet
from birdclef.data.utils import slice_seconds
from birdclef.utils import spark_resource
from workflows.convert_audio.ogg_to_mp3 import ToMP3Single
from workflows.mixit.docker import MixitDockerTask
from workflows.utils.gcs import single_file_target
from workflows.utils.mixin import DynamicRequiresMixin
from workflows.utils.rsync import GSUtilRsyncTask


class PadAudioNoise(luigi.Task, DynamicRequiresMixin):
    input_path = luigi.Parameter()
    output_path = luigi.Parameter()
    track_name = luigi.Parameter()
    noise_alpha = luigi.FloatParameter(default=0.1)

    def output(self):
        return single_file_target(
            Path(self.output_path) / self.track_name.replace(".ogg", ".wav")
        )

    def run(self):
        path = Path(self.input_path) / self.track_name
        y, sr = librosa.load(path.as_posix(), sr=48_000, mono=True)

        # lets generate noise using the same distribution as the signal. The shape
        # should be rounded up the the nearest 3rd second.
        noise_shape = (int(y.shape[0] / sr // 3) + 1) * 3 * sr
        noise = np.random.normal(loc=y.mean(), scale=y.std(), size=noise_shape)

        # lets add the noise to the signal via weighted average, making the noise 10% of the signal
        zero_pad_y = np.zeros(noise_shape)
        # now place the signal in the center of the padding
        start = (noise_shape - y.shape[0]) // 2
        end = start + y.shape[0]
        zero_pad_y[start:end] = y

        y_noise = (zero_pad_y * 0.9) + (noise * 0.1)

        # now lets write the file
        output_path = Path(self.output().path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # write this as a temporary wav file
        sf.write(output_path, y_noise, sr)

        # wait for the file to be written up to 10 seconds
        for i in range(20):
            if output_path.exists():
                break
            time.sleep(0.5)


class ExtractEmbedding(luigi.Task, DynamicRequiresMixin):
    input_path = luigi.Parameter()
    output_path = luigi.Parameter()
    track_name = luigi.Parameter()
    birdnet_root_path = luigi.Parameter()
    parallelism = luigi.IntParameter(default=2)

    @property
    def track_stem(self):
        return self.track_name.replace(".ogg", "")

    def output(self):
        return single_file_target(Path(self.output_path) / self.track_stem / "_SUCCESS")

    def process_audio_files(
        self,
        paths,
        prediction_func,
        labels,
        mapped_labels,
        sr=48_000,
    ):
        for path in tqdm.tqdm(paths):
            y, sr = librosa.load(path.as_posix(), sr=sr, mono=True)
            X = slice_seconds(y, sr, seconds=3, step=3)
            pred = prediction_func(X)[0]
            pred_sigmoid = 1 / (1 + np.exp(-pred))

            indices = birdnet.rank_indices(pred_sigmoid)
            for i in range(pred_sigmoid.shape[0]):
                predictions = [
                    {
                        "index": int(j),
                        "label": labels[j],
                        "mapped_label": mapped_labels[j],
                        "probability": float(pred_sigmoid[i][j]),
                    }
                    for rank, j in enumerate(indices)
                ]
                # sort and add an index for the rank, because each segment
                # is ranked by the most common species across the entire
                # segment
                predictions = [
                    Row(rank=rank, **row)
                    for rank, row in enumerate(
                        sorted(predictions, key=lambda row: -row["probability"])
                    )
                ]
                yield Row(
                    **{
                        "species": path.parts[-2],
                        "track_stem": path.stem.split("_")[0],
                        "track_type": (
                            path.stem.split("_")[-1] if "_" in path.stem else ""
                        ),
                        "track_name": "/".join(path.parts[-2:]),
                        "embedding": pred[i].tolist(),
                        "predictions": predictions,
                        "start_time": i * 3,
                    }
                )

    def run(self):
        # load the model
        repo_path = self.birdnet_root_path
        model = birdnet.load_model_from_repo(repo_path)
        prediction_func = birdnet.prediction_func(model)
        labels = birdnet.load_labels(repo_path)
        mapped_labels = birdnet.load_mapped_labels(repo_path)

        # find all the audio files to process

        # load the audio file
        paths = sorted(Path(self.input_path).glob(f"{self.track_stem}*.mp3"))
        rows = list(
            self.process_audio_files(paths, prediction_func, labels, mapped_labels)
        )
        # now with spark, lets write the parquet file
        with spark_resource(cores=self.parallelism) as spark:
            df = spark.createDataFrame(rows)
            assert df.count() > 0, "No rows found in dataframe"
            df.repartition(1).write.parquet(
                # the output is the success file, but we want the parent directory
                Path(self.output().path).parent.as_posix(),
                mode="overwrite",
            )


class TrackWorkflow(luigi.Task):
    birdclef_root_path = luigi.Parameter()
    output_path = luigi.Parameter()
    birdnet_root_path = luigi.Parameter()
    track_name = luigi.Parameter()

    def output(self):
        return single_file_target(
            Path(self.output_path)
            / "embeddings"
            / self.track_name.replace(".ogg", "")
            / "_SUCCESS"
        )

    def run(self):
        pad_noise = PadAudioNoise(
            input_path=f"{self.birdclef_root_path}/train_audio",
            output_path=f"{self.output_path}/audio",
            track_name=self.track_name,
        )
        yield pad_noise

        wav_track_name = self.track_name.replace(".ogg", ".wav")

        convert_mp3 = ToMP3Single(
            input_path=f"{self.output_path}/audio",
            output_path=f"{self.output_path}/audio",
            track_name=wav_track_name,
            input_ext=".wav",
            dynamic_requires=[pad_noise],
        )

        mixit = MixitDockerTask(
            input_path=f"{self.output_path}/audio",
            output_path=f"{self.output_path}/audio",
            track_name=wav_track_name,
            num_sources=4,
            dynamic_requires=[pad_noise],
        )
        yield [convert_mp3, mixit]

        extract_embedding = ExtractEmbedding(
            input_path=f"{self.output_path}/audio",
            output_path=f"{self.output_path}/embeddings",
            track_name=self.track_name,
            birdnet_root_path=self.birdnet_root_path,
            dynamic_requires=[pad_noise, convert_mp3, mixit],
        )
        yield extract_embedding


class SpeciesWorkflow(luigi.WrapperTask):
    birdclef_root_path = luigi.Parameter()
    output_path = luigi.Parameter()
    birdnet_root_path = luigi.Parameter()
    species = luigi.Parameter()
    limit = luigi.IntParameter(default=-1)

    def requires(self):
        species_root = Path(self.birdclef_root_path) / "train_audio" / self.species
        track_names = sorted(
            ["/".join(p.parts[-2:]) for p in species_root.glob("*.ogg")]
        )
        if self.limit > 0:
            track_names = track_names[: self.limit]
        for track_name in track_names:
            yield TrackWorkflow(
                birdclef_root_path=self.birdclef_root_path,
                output_path=self.output_path,
                birdnet_root_path=self.birdnet_root_path,
                track_name=track_name,
            )


if __name__ == "__main__":
    birdclef_root_path = "data/raw/birdclef-2023"
    output_path = "data/processed/birdclef-2023/train_embeddings"
    birdnet_root_path = "data/models/birdnet-analyzer-pruned"
    species_limit = -1

    train_audio_root = Path(birdclef_root_path) / "train_audio"
    species = sorted([p.name for p in train_audio_root.glob("*")])

    for s in species[:1]:
        luigi.build(
            [
                SpeciesWorkflow(
                    birdclef_root_path=birdclef_root_path,
                    output_path=output_path,
                    birdnet_root_path=birdnet_root_path,
                    species=s,
                    limit=4,
                )
            ],
            workers=max(int(os.cpu_count() / 2), 1),
            scheduler_host="luigi.us-central1-a.c.birdclef-2023.internal",
            log_level="INFO",
        )

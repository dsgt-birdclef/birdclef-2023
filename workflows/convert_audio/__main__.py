import os
from pathlib import Path

import luigi
from google.cloud import storage

from workflows.convert_audio.ogg_to_mp3 import OggToMP3
from workflows.utils.pull import Pull
from workflows.utils.push import Push


class ConvertAudioTask(luigi.WrapperTask):
    """Wrapper around the entire DAG."""

    birdclef_root_path = luigi.Parameter()
    intermediate_path = luigi.Parameter()
    output_path = luigi.Parameter()

    n_threads = luigi.IntParameter(default=4)
    parallelism = luigi.IntParameter(default=os.cpu_count())

    def list_species(self):
        storage_client = storage.Client("birdclef-2023")

        bucket = storage_client.get_bucket("birdclef-2023")
        # Note: Client.list_blobs requires at least package version 1.17.0.
        # Use input path "data/raw/birdclef-2022/train_audio/species"
        species = bucket.list_blobs(prefix=self.birdclef_root_path)

        species_list = []
        for blob in species:
            name = blob.name
            name = name.replace(self.birdclef_root_path + "/", "")
            name = name.split("/")[0]
            species_list.append(name)

        return list(set(species_list))

    def requires(self):
        species_list = self.list_species()

        for species in species_list[0:1]:
            species = species.strip()

            pull_data = Pull(
                input_path=os.path.join(self.birdclef_root_path, species),
                output_path=os.path.join(self.intermediate_path, "ogg", species),
                parallelism=self.parallelism,
            )
            yield pull_data

            ogg_to_mp3 = OggToMP3(
                input_path=os.path.join(self.intermediate_path, "ogg", species),
                output_path=os.path.join(self.intermediate_path, "mp3", species),
                parallelism=self.parallelism,
                dynamic_requires=[pull_data],
            )
            yield ogg_to_mp3

            push_data = Push(
                input_path=os.path.join(self.intermediate_path, "mp3", species),
                output_path=os.path.join(self.output_path, species),
                parallelism=self.parallelism,
                dynamic_requires=[pull_data, ogg_to_mp3],
            )
            yield push_data


if __name__ == "__main__":
    n_threads = 16
    luigi.build(
        [
            ConvertAudioTask(
                birdclef_root_path="data/raw/birdclef-2022/train_audio",
                intermediate_path="data/raw/birdclef-2022/train_audio",
                output_path="data/processed/birdclef-2022/mp3",
                n_threads=n_threads,
                parallelism=os.cpu_count(),
            ),
        ],
        local_scheduler=True,
        workers=os.cpu_count() // n_threads,
    )

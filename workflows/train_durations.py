import os
import tempfile
from multiprocessing import Pool
from pathlib import Path

import librosa
import luigi
import pandas as pd
from tqdm import tqdm
from workflow.utils.rsync import GSUtilRsyncTask

from workflows.utils.mixin import DynamicRequiresMixin


def read_path(path: Path) -> dict:
    y, sr = librosa.load(path)
    duration = librosa.get_duration(y=y, sr=sr)
    return dict(filename="/".join(path.parts[-2:]), duration=duration)


class TrainDurations(luigi.Task, DynamicRequiresMixin):
    """Get the duration of each song in the training set into a parquet file."""

    birdclef_root_path = luigi.Parameter()
    output_path = luigi.Parameter()
    parallelism = luigi.IntParameter(default=os.cpu_count())
    capture_output = True

    def requires(self):
        return self.dynamic_requires

    def output(self):
        return luigi.LocalTarget(self.output_path)

    def run(self):
        paths = sorted(Path(self.birdclef_root_path).glob("train_audio/**/*.ogg"))
        with Pool(self.parallelism) as pool:
            res = list(tqdm(pool.imap(read_path, paths), total=len(paths)))

        df = pd.DataFrame(res)
        print(df.head())
        # ensure the output directory exists
        Path(self.output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(self.output_path)


class TrainDurationsWorkflow(luigi.WrapperTask):
    birdclef_root_path = luigi.Parameter()
    output_path = luigi.Parameter()
    parallelism = luigi.IntParameter(default=os.cpu_count())

    def requires(self):
        # create a temporary path to download the data, make it persistent since
        # we're only wrapping the task here
        tmp_path = Path(tempfile.mkdtemp())
        tmp_birdclef_root_path = tmp_path / "audio_root"
        tmp_output_path = tmp_path / "train_durations.parquet"

        download_task = GSUtilRsyncTask(
            input_path=self.birdclef_root_path,
            output_path=tmp_birdclef_root_path.as_posix(),
        )
        yield download_task

        train_durations = TrainDurations(
            birdclef_root_path=tmp_birdclef_root_path.as_posix(),
            output_path=tmp_output_path.as_posix(),
            parallelism=self.parallelism,
            dynamic_requires=[download_task],
        )
        yield train_durations

        upload_task = GSUtilRsyncTask(
            input_path=tmp_output_path.as_posix(),
            output_path=self.output_path,
            is_dir=False,
            dynamic_requires=[train_durations],
        )
        yield upload_task


if __name__ == "__main__":
    luigi.build(
        [
            TrainDurations(
                birdclef_root_path="data/raw/birdclef-2022",
                output_path="data/processed/birdclef-2022/train_durations.parquet",
            )
        ],
        log_level="INFO",
    )

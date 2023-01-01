import luigi

import librosa
import pandas as pd
from tqdm import tqdm
import os
from pathlib import Path
from multiprocessing import Pool


def read_path(path: Path) -> dict:
    y, sr = librosa.load(path)
    duration = librosa.get_duration(y=y, sr=sr)
    return dict(filename="/".join(path.parts[-2:]), duration=duration)


class TrainDurations(luigi.Task):
    """Get the duration of each song in the training set into a parquet file."""

    birdclef_root_path = luigi.Parameter()
    output_path = luigi.Parameter()
    parallelism = luigi.IntParameter(default=os.cpu_count())
    capture_output = True

    def requires(self):
        return []

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

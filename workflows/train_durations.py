import luigi
from luigi.contrib.external_program import ExternalProgramTask


class TrainDurations(ExternalProgramTask):
    """Get the duration of each song in the training set into a parquet file."""

    birdclef_root_path = luigi.Parameter()
    output_path = luigi.Parameter()
    capture_output = True

    def requires(self):
        return []

    def output(self):
        return luigi.LocalTarget(self.output_path)

    def program_args(self):
        return [
            "python",
            "scripts/train_durations.py",
            self.birdclef_root_path,
            self.output_path,
        ]


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

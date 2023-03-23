import os
from pathlib import Path

import librosa
import luigi
import pandas as pd

from birdclef.utils import spark_resource
from workflows.utils.gcs import single_file_target

from .docker import MixitDockerTask


class GetTrackSubset(luigi.Task):
    durations_path = luigi.Parameter()
    output_path = luigi.Parameter()
    limit = luigi.IntParameter(default=16)
    parallelism = luigi.IntParameter(default=os.cpu_count(), significant=False)

    def output(self):
        return single_file_target(self.output_path)

    def run(self):
        with spark_resource(cores=self.parallelism) as spark:
            df = spark.read.parquet(self.durations_path)
            subset = (
                df.where("duration > 29 and duration < 31")
                .orderBy("duration")
                .limit(self.limit)
            )
            # ensure folder exists
            Path(self.output().path).parent.mkdir(parents=True, exist_ok=True)
            subset.toPandas().to_json(self.output().path, orient="records")


class MixitWrapperTask(luigi.WrapperTask):
    birdclef_root_path = luigi.Parameter()
    track_subset_path = luigi.Parameter()
    output_path = luigi.Parameter()

    def requires(self):
        track_subset_df = pd.read_json(self.track_subset_path)
        for row in track_subset_df.itertuples():
            task = MixitDockerTask(
                birdclef_root_path=self.birdclef_root_path,
                output_path=f"{self.output_path}/audio",
                track_name=row.filename,
                num_sources=4,
            )
            yield task


# lets create a task that runs mixit on our subset of data
class VisualizeSubsetWorkflow(luigi.Task):
    birdclef_root_path = luigi.Parameter()
    durations_path = luigi.Parameter()
    output_path = luigi.Parameter()
    limit = luigi.IntParameter(default=16)

    def run(self):
        track_subset = GetTrackSubset(
            durations_path=self.durations_path,
            output_path=f"{self.output_path}/subset.json",
            limit=self.limit,
        )
        yield track_subset

        yield MixitWrapperTask(
            birdclef_root_path=self.birdclef_root_path,
            track_subset_path=track_subset.output().path,
            output_path=self.output_path,
        )


if __name__ == "__main__":
    luigi.build(
        [
            VisualizeSubsetWorkflow(
                birdclef_root_path="data/raw/birdclef-2023",
                durations_path="gs://birdclef-2023/data/processed/birdclef-2023/train_durations_v2.parquet",
                output_path="data/processed/mixit_visualize_subset",
            )
        ],
        workers=max(os.cpu_count() // 2, 1),
        scheduler_host="luigi.us-central1-a.c.birdclef-2023.internal",
        log_level="INFO",
    )

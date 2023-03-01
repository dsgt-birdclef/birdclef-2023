import os
from multiprocessing import Pool
from pathlib import Path

import luigi
from google.cloud import storage
from luigi.contrib.gcs import GCSClient, GCSFlagTarget
from luigi.parameter import ParameterVisibility


class Push(luigi.Task):
    input_path = luigi.Parameter()
    output_path = luigi.Parameter()
    parallelism = luigi.IntParameter(default=os.cpu_count(), significant=False)
    dynamic_requires = luigi.Parameter(
        default=[], visibility=ParameterVisibility.HIDDEN
    )

    def output(self):
        filepath = "gs://birdclef-2023/" + self.output_path
        return GCSFlagTarget(path=filepath + "/", client=GCSClient(), flag="_SUCCESS")

    def upload_track(self, filename):
        storage_client = storage.Client("birdclef-2023")

        bucket = storage_client.get_bucket("birdclef-2023")
        # Note: Client.list_blobs requires at least package version 1.17.0.
        # Use input path "data/raw/birdclef-2022/train_audio/species"
        blob = bucket.blob(filename)
        blob.upload_from_filename(os.join.path(self.input_path / filename))

        return

    def list_tracks(self):
        list_tracks = os.listdir(self.input_path)

        return list_tracks

    def requires(self):
        return self.dynamic_requires

    def run(self):
        self.output_path = Path(self.output_path)
        self.input_path = Path(self.input_path)

        tracks = self.list_tracks()
        for track_file in tracks:
            name = str(track_file.name).split("/")[-1]

            self.upload_track(name)

        storage_client = storage.Client("birdclef-2023")

        bucket = storage_client.get_bucket("birdclef-2023")
        # Note: Client.list_blobs requires at least package version 1.17.0.
        # Use input path "data/raw/birdclef-2022/train_audio/species"
        blob = bucket.blob("_SUCCESS")
        blob.upload_from_filename(self.input_path / filename)

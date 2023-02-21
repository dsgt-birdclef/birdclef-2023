import os
from multiprocessing import Pool
from pathlib import Path

import luigi
from google.cloud import storage
from luigi.parameter import ParameterVisibility
from pydub import AudioSegment


class OggToMP3(luigi.Task):
    input_path = luigi.Parameter()
    output_path = luigi.Parameter()
    parallelism = luigi.IntParameter(default=os.cpu_count(), significant=False)

    def output(self):
        return luigi.LocalTarget(self.output_path)

    def list_images(self):
        # storage_client = storage.Client()

        # Note: Client.list_blobs requires at least package version 1.17.0.
        # images = storage_client.list_blobs(self.input_path)
        images = os.listdir(self.input_path)

        return images

    def requires(self):
        return None

    def load_ogg(self, ofn):
        x = AudioSegment.from_file(ofn)

        return x

    def run(self):
        tracks = self.list_images()

        self.output_path = Path(self.output_path)
        self.input_path = Path(self.input_path)

        if not os.path.isdir(self.output_path):
            self.output_path.mkdir(parents=True, exist_ok=True)
        for track_file in tracks:
            track_audio = self.load_ogg(self.input_path / track_file)
            new_file = track_file.replace(".ogg", ".mp3")

            new_file = new_file.split("/")[-1]
            track_audio.export(
                self.output_path / new_file,
                format="mp3",
                parameters=["-q:a", "5"],
            )

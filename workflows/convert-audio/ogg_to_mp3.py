import os
from multiprocessing import Pool
from pathlib import Path

import luigi
from google.cloud import storage
from luigi.parameter import ParameterVisibility
from pull import Pull
from pydub import AudioSegment


class OggToMP3(luigi.Task):
    input_path = luigi.Parameter()
    output_path = luigi.Parameter()
    parallelism = luigi.IntParameter(default=os.cpu_count(), significant=False)

    def output(self):
        return luigi.LocalTarget(self.output_path)

    def requires(self):
        return self.dynamic_requires

    def load_ogg(self, ofn):
        x = AudioSegment.from_file(ofn)

        return x
    
    def list_tracks(self):
        list_tracks = os.listdir(self.input_path)

        return list_tracks

    def run(self):
        self.output_path = Path(self.output_path)
        self.input_path = Path(self.input_path)

        tracks = self.list_images()

        if not self.output_path.is_dir():
            self.output_path.mkdir(parents=True, exist_ok=True)
        for track_file in tracks:
            track_audio = self.load_ogg(self.input_path / track_file)

            new_file = str(track_file).replace(".ogg", ".mp3")

            new_file = new_file.split("/")[-1]
            track_audio.export(
                self.output_path / new_file,
                format="mp3",
                parameters=["-q:a", "5"],
            )

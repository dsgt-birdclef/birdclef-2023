import os
from multiprocessing import Pool
from pathlib import Path

import luigi
from google.cloud import storage
from list_species import ListSpecies
from luigi.parameter import ParameterVisibility
from pydub import AudioSegment


class Pull(luigi.Task):
    input_path = luigi.Parameter()
    text_output_path = luigi.Parameter()
    output_path = luigi.Parameter()
    parallelism = luigi.IntParameter(default=os.cpu_count(), significant=False)

    def output(self):
        return luigi.LocalTarget(self.output_path)

    def list_tracks(self, species):
        storage_client = storage.Client("birdclef-2023")

        bucket = storage_client.get_bucket("birdclef-2023")
        # Note: Client.list_blobs requires at least package version 1.17.0.
        # Use input path "data/raw/birdclef-2022/train_audio/species"
        tracks = bucket.list_blobs(prefix=os.path.join(self.input_path, species))

        return tracks

    def requires(self):
        return ListSpecies(self.input_path, self.text_output_path)

    def read_list(self):
        with open(self.text_output_path, "r") as f:
            lines = f.read().splitlines()

        return lines

    def run(self):
        species_list = self.read_list()

        for species in species_list:
            tracks = self.list_tracks(species)

            self.output_path = Path(self.output_path) / "species"
            self.input_path = Path(self.input_path)

            if not self.output_path.is_dir():
                self.output_path.mkdir(parents=True, exist_ok=True)
            for track_file in tracks:
                name = str(track_file.name).split("/")[-1]

                track_file.download_to_filename(self.output_path / name)

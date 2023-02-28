import os
from multiprocessing import Pool
from pathlib import Path

import luigi
from google.cloud import storage
from luigi.parameter import ParameterVisibility


class ListSpecies(luigi.Task):
    input_path = luigi.Parameter()
    text_output_path = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.text_output_path)

    def list_species(self):
        storage_client = storage.Client("birdclef-2023")

        bucket = storage_client.get_bucket("birdclef-2023")
        # Note: Client.list_blobs requires at least package version 1.17.0.
        # Use input path "data/raw/birdclef-2022/train_audio/species"
        species = bucket.list_blobs(prefix=self.input_path)

        species_list = []
        for blob in species:
            name = blob.name
            name = name.replace(self.input_path + "/", "")
            name = name.split("/")[0]
            species_list.append(name)

        return list(set(species_list))

    def requires(self):
        return None

    def run(self):
        species_list = self.list_species()

        file = open(self.text_output_path, "w")
        for species in species_list:
            file.write(species + "\n")
        file.close()

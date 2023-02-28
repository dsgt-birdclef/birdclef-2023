import os
import sys
from pathlib import Path

sys.path.insert(1, "workflows/utils")

import luigi
from list_species import ListSpecies
from ogg_to_mp3 import OggToMP3
from pull import Pull
from push import Push


class ConvertAudioTask(luigi.WrapperTask):
    """Wrapper around the entire DAG."""

    birdclef_root_path = luigi.Parameter()

    text_file_path = luigi.Parameter()

    intermediate_path = luigi.Parameter()

    output_path = luigi.Parameter()

    n_threads = luigi.IntParameter(default=4)
    parallelism = luigi.IntParameter(default=os.cpu_count())

    def requires(self):
        list_species_task = ListSpecies(
            input_path=self.birdclef_root_path,
            text_output_path=self.text_file_path,
        )
        yield list_species_task

        with open(self.text_file_path, "r") as f:
            species_list = f.read().splitlines()

        for species in species_list:
            species = species.strip()

            pull_data = Pull(
                input_path=self.birdclef_root_path / species,
                output_path=self.intermediate_path / "ogg" / species,
                parallelism=self.parallelism,
                dynamic_requires=[list_species_task],
            )
            yield pull_data

            ogg_to_mp3 = OggToMP3(
                input_path=self.intermediate_path / "ogg" / species,
                output_path=self.intermediate_path / "mp3" / species,
                parallelism=self.parallelism,
                dynamic_requires=[pull_data],
            )
            yield ogg_to_mp3

            push_data = push(
                input_path=self.intermediate_path / "mp3" / species,
                output_path=self.output_path / species,
                parallelism=self.parallelism,
                dynamic_requires=[ogg_to_mp3],
            )
            yield push_data


if __name__ == "__main__":
    n_threads = 16
    luigi.build(
        [
            ConvertAudioTask(
                birdclef_root_path="data/raw/birdclef-2022/train_audio",
                text_file_path="data/raw/birdclef-2022/train_audio/species.txt",
                intermediate_path="data/raw/birdclef-2022/train_audio",
                output_path="data/processed/birdclef-2022/mp3",
                n_threads=n_threads,
                parallelism=os.cpu_count(),
            ),
        ],
        local_scheduler=True,
        workers=os.cpu_count() // n_threads,
    )

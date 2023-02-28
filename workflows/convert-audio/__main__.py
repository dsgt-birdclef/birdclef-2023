import os
from pathlib import Path

import luigi

from .ogg_to_mp3 import OggToMP3
from birdclef.workflows.utils.list_species import ListSpecies
from birdclef.workflows.utils.pull import Pull
from birdclef.workflows.utils.push import Push



class ConvertAudioTask(luigi.WrapperTask):
    """Wrapper around the entire DAG."""

    birdclef_root_path = luigi.Parameter()
    birdclef_root_path = Path(birdclef_root_path)

    text_file_path = luigi.Parameter()
    text_file_path = Path(text_file_path)

    intermediate_path = luigi.Parameter()
    intermediate_path = Path(intermediate_path)

    output_path = luigi.Parameter()
    output_path = Path(output_path)

    n_threads = luigi.IntParameter(default=4)
    parallelism = luigi.IntParameter(default=os.cpu_count())

    def requires(self):
        list_species_task = ListSpecies(
            input_path=self.birdclef_root_path,
            text_output_path=self.text_file_path,
        )
        yield list_species_task

        with open(self.text_output_path, "r") as f:
            species_list = f.read().splitlines()

        for species in species_list:
            species = species.strip()
                
            pull_data = Pull(
                input_path=self.birdclef_root_path / species
                output_path=self.intermediate_path / "ogg" / species,
                parallelism=self.parallelism,
                dynamic_requires=[list_species_task]
            )
            yield pull_data

            ogg_to_mp3 = OggToMP3(
                input_path=self.intermediate_path / "ogg" / species,
                output_path=self.intermediate_path / "mp3" / species,
                parallelism=self.parallelism,
                dynamic_requires=[pull_data]
            )
            yield ogg_to_mp3

            push_data = push(
                input_path=self.intermediate_path / "mp3" / species,
                output_path=self.output_path,
                parallelism=self.parallelism,
                dynamic_requires=[ogg_to_mp3],
            )
            yield push_data


if __name__ == "__main__":
    n_threads = 16
    luigi.build(
        [
            ConvertAudioTask(
                birdclef_root_path="data/raw/birdclef-2022",
                intermediate_path="data/intermediate/birdclef-2022",
                output_path="data/processed/birdclef-2022",
                n_threads=n_threads,
                parallelism=os.cpu_count(),
            ),
        ],
        workers=os.cpu_count() // n_threads,
    )

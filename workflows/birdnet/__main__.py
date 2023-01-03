import os

import luigi

from .docker import BirdNetAnalyzeTaskAllTask, BirdNetEmbeddingsTaskAllTask
from .preprocess import BirdNetAnalyzeConcatTask, BirdNetEmbeddingsConcatTask


class BirdNetTask(luigi.WrapperTask):
    """Wrapper around the entire DAG."""

    birdclef_root_path = luigi.Parameter()
    intermediate_path = luigi.Parameter()
    output_path = luigi.Parameter()
    n_threads = luigi.IntParameter(default=4)
    parallelism = luigi.IntParameter(default=os.cpu_count())

    def requires(self):
        analyze_task = BirdNetAnalyzeTaskAllTask(
            birdclef_root_path=self.birdclef_root_path,
            output_path=f"{self.intermediate_path}/birdnet/analyze",
        )
        yield analyze_task

        yield BirdNetAnalyzeConcatTask(
            taxonomy_path=f"{self.birdclef_root_path}/eBird_Taxonomy_v2021.csv",
            input_path=f"{self.intermediate_path}/birdnet/analyze",
            output_path=self.output_path,
            parallelism=self.parallelism,
            dynamic_requires=[analyze_task],
        )

        emb_task = BirdNetEmbeddingsTaskAllTask(
            birdclef_root_path=self.birdclef_root_path,
            output_path=f"{self.intermediate_path}/birdnet/embeddings",
            n_threads=n_threads,
        )
        yield emb_task

        yield BirdNetEmbeddingsConcatTask(
            input_path=f"{self.intermediate_path}/birdnet/embeddings",
            output_path=self.output_path,
            parallelism=self.parallelism,
            dynamic_requires=[emb_task],
        )


if __name__ == "__main__":
    n_threads = 16
    luigi.build(
        [
            BirdNetTask(
                birdclef_root_path="data/raw/birdclef-2022",
                intermediate_path="data/intermediate/birdclef-2022",
                output_path="data/processed/birdclef-2022",
                n_threads=n_threads,
                parallelism=os.cpu_count(),
            ),
        ],
        workers=os.cpu_count() // n_threads,
    )

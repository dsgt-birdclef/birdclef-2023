import os
import tempfile
from functools import partial
from multiprocessing import Pool
from pathlib import Path

import luigi
import numpy as np
import pandas as pd
from luigi.contrib.docker_runner import DockerTask
from luigi.parameter import ParameterVisibility
from pyspark.sql import functions as F
from tqdm import tqdm

from birdclef.utils import spark_resource


class BirdNetAnalyzeTask(DockerTask):
    """Run BirdNet on the training set."""

    birdclef_root_path = luigi.Parameter()
    output_path = luigi.Parameter()
    species = luigi.Parameter()
    n_threads = luigi.IntParameter(default=4)

    image = "us-central1-docker.pkg.dev/birdclef-2023/birdclef-2023/birdnet:latest"
    environment = {"NUMBA_CACHE_DIR": "/tmp"}
    container_options = {
        "user": f"{os.getuid()}:{os.getgid()}",
    }

    @property
    def staging_path(self):
        # a singleton variable that's set on the first call, hacky solution
        if not hasattr(self, "_staging_path"):
            self._staging_path = Path(tempfile.mkdtemp())
        return self._staging_path

    @property
    def binds(self):
        root = Path("./data").absolute()

        # create a temporary file to mount as the error log
        _, error_log_path = tempfile.mkstemp()

        return [
            f"{root}:/mnt/data",
            f"{self.staging_path}:/mnt/staging_output",
            # we also need to somehow allow the errors to be written
            f"{error_log_path}:/error_log.txt",
        ]

    def requires(self):
        return []

    def output(self):
        return luigi.LocalTarget(f"{self.output_path}/{self.species}")

    @property
    def command(self):
        return " ".join(
            [
                "analyze.py",
                f"--i /mnt/{self.birdclef_root_path}/train_audio/{self.species}",
                f"--o /mnt/staging_output",
                f"--threads {self.n_threads}",
                "--rtype csv",
            ]
        )

    def run(self):
        super().run()
        # move the intermediate results to the output, ensuring parents exist
        self.output().makedirs()
        print(f"Moving {self.staging_path} to {self.output().path}")
        Path(self.staging_path).rename(self.output().path)


class BirdNetEmbeddingsTask(BirdNetAnalyzeTask):
    @property
    def command(self):
        return " ".join(
            [
                "embeddings.py",
                f"--i /mnt/{self.birdclef_root_path}/train_audio/{self.species}",
                f"--o /mnt/staging_output",
                f"--threads {self.n_threads}",
                "--batchsize 16",
            ]
        )


# wrapper task to run BirdNet on all species
class BirdNetAnalyzeTaskAllTask(luigi.WrapperTask):
    birdclef_root_path = luigi.Parameter()
    output_path = luigi.Parameter()
    n_threads = luigi.IntParameter(default=4)
    limit = luigi.IntParameter(default=None)

    upstream_task_type = BirdNetAnalyzeTask

    def requires(self):
        species = sorted(
            [p.name for p in Path(f"{self.birdclef_root_path}/train_audio").glob("*")]
        )
        if self.limit is not None:
            species = species[: self.limit]
        for specie in species:
            yield self.upstream_task_type(
                birdclef_root_path=self.birdclef_root_path,
                output_path=self.output_path,
                species=specie,
                n_threads=self.n_threads,
            )


class BirdNetEmbeddingsTaskAllTask(BirdNetAnalyzeTaskAllTask):
    upstream_task_type = BirdNetEmbeddingsTask


class BirdNetAnalyzeConcatTask(luigi.Task):
    taxonomy_path = luigi.Parameter()
    input_path = luigi.Parameter()
    output_path = luigi.Parameter()
    parallelism = luigi.IntParameter(default=os.cpu_count())
    dynamic_requires = luigi.Parameter(default=[])

    def requires(self):
        return self.dynamic_requires

    def output(self):
        return luigi.LocalTarget(f"{self.output_path}/birdnet-analyze.parquet")

    def read_path(self, path: Path, lookup=lambda x: x) -> pd.DataFrame:
        df = pd.read_csv(path)
        name = path.name.split(".")[0]
        df["filename"] = f"{path.parent.name}/{name}.ogg"
        df["birdnet_label"] = df["Common name"].apply(lambda x: lookup(x, "unknown"))
        df["birdnet_common_name"] = df["Common name"]
        return df

    def run(self):
        taxonomy_df = pd.read_csv(self.taxonomy_path)
        common_to_code = dict(
            list(zip(taxonomy_df["PRIMARY_COM_NAME"], taxonomy_df["SPECIES_CODE"]))
        )

        root = Path(self.input_path)
        paths = sorted(root.glob("**/*.csv"))
        with Pool(self.parallelism) as pool:
            res = list(
                tqdm(
                    pool.imap(
                        partial(self.read_path, lookup=common_to_code.get), paths
                    ),
                    total=len(paths),
                )
            )
        df = pd.concat(res).rename(
            columns={
                "Start (s)": "start_sec",
                "End (s)": "end_sec",
                "Confidence": "confidence",
            }
        )[
            [
                "start_sec",
                "end_sec",
                "confidence",
                "birdnet_label",
                "birdnet_common_name",
                "filename",
            ]
        ]
        print(df.head())
        # ensure the output directory exists
        output_path = Path(self.output().path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)


class BirdNetEmbeddingsConcatTask(luigi.Task):
    """Concatenate embeddings into a single file using PySpark."""

    input_path = luigi.Parameter()
    output_path = luigi.Parameter()
    parallelism = luigi.IntParameter(default=os.cpu_count())
    partitions = luigi.IntParameter(default=8)
    dynamic_requires = luigi.Parameter(default=[])

    def requires(self):
        return self.dynamic_requires

    def output(self):
        return luigi.LocalTarget(f"{self.output_path}/birdnet-embeddings.parquet")

    def run(self):
        def parse_meta_path(path: str) -> dict:
            species, name = Path(path).parts[-2:]
            # name is like {ID}.birdnet.embeddings.txt
            id = name.split(".")[0]
            return dict(species=species, id=id)

        def parse_emb_text(emb_text: str) -> np.ndarray:
            return np.fromstring(emb_text, dtype=float, sep=",").tolist()

        with spark_resource(cores=self.parallelism) as spark:
            df = (
                spark.read.csv(
                    f"{self.input_path}/*/*.txt",
                    sep="\t",
                    schema="start_sec FLOAT, end_sec FLOAT, emb_text STRING",
                )
                .withColumn(
                    "path",
                    F.udf(parse_meta_path, "struct<species: string, id: string>")(
                        F.input_file_name()
                    ),
                )
                .select(
                    "start_sec",
                    "end_sec",
                    "path.*",
                    F.udf(parse_emb_text, "array<float>")("emb_text").alias("emb"),
                )
                .orderBy("species", "id", "start_sec")
            )
            df.printSchema()
            df.show(3, vertical=True)
            df.toPandas().to_parquet(self.output().path, index=False)


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

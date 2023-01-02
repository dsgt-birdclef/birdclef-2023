import os
import tempfile
from functools import partial
from multiprocessing import Pool
from pathlib import Path

import luigi
import pandas as pd
from luigi.contrib.docker_runner import DockerTask
from tqdm import tqdm


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
    def binds(self):
        root = Path("./data").absolute()

        # create a temporary file to mount as the error log
        _, error_log_path = tempfile.mkstemp()

        return [
            f"{root}:/mnt/data",
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
                f"--o /mnt/{self.output().path}",
                f"--threads {self.n_threads}",
                "--rtype csv",
            ]
        )


# wrapper task to run BirdNet on all species
class BirdNetAnalyzeTaskAllTask(luigi.WrapperTask):
    birdclef_root_path = luigi.Parameter()
    output_path = luigi.Parameter()
    n_threads = luigi.IntParameter(default=4)

    def requires(self):
        species = [
            p.name for p in Path(f"{self.birdclef_root_path}/train_audio").glob("*")
        ]
        for specie in species:
            yield BirdNetAnalyzeTask(
                birdclef_root_path=self.birdclef_root_path,
                output_path=self.output_path,
                species=specie,
                n_threads=self.n_threads,
            )


class BirdNetAnalyzeConcatTask(luigi.Task):
    birdclef_root_path = luigi.Parameter()
    taxonomy_path = luigi.Parameter()
    input_path = luigi.Parameter()
    output_path = luigi.Parameter()
    parallelism = luigi.IntParameter(default=os.cpu_count())

    def requires(self):
        return [
            BirdNetAnalyzeTaskAllTask(
                birdclef_root_path=self.birdclef_root_path,
                output_path=self.input_path,
            )
        ]

    def output(self):
        return luigi.LocalTarget(f"{self.output_path}/birdnet-analysis.parquet")

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


class BirdNetTask(luigi.WrapperTask):
    """Wrapper around the entire DAG."""

    birdclef_root_path = luigi.Parameter()
    intermediate_path = luigi.Parameter()
    output_path = luigi.Parameter()
    n_threads = luigi.IntParameter(default=4)
    parallelism = luigi.IntParameter(default=os.cpu_count())

    def requires(self):
        yield BirdNetAnalyzeTaskAllTask(
            birdclef_root_path=self.birdclef_root_path,
            output_path=f"{self.intermediate_path}/birdnet/analysis",
        )
        yield BirdNetAnalyzeConcatTask(
            birdclef_root_path=self.birdclef_root_path,
            taxonomy_path=f"{self.birdclef_root_path}/eBird_Taxonomy_v2021.csv",
            input_path=f"{self.intermediate_path}/birdnet/analysis",
            output_path=self.output_path,
            parallelism=self.parallelism,
        )


if __name__ == "__main__":
    n_threads = 4
    luigi.build(
        [
            BirdNetTask(
                birdclef_root_path="data/raw/birdclef-2022",
                intermediate_path="data/intermediate/birdclef-2022",
                output_path="data/processed/birdclef-2022",
                n_threads=n_threads,
                parallelism=os.cpu_count(),
            )
        ],
        workers=os.cpu_count() // n_threads,
    )

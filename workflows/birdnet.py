import luigi
from luigi.contrib.docker_runner import DockerTask
from pathlib import Path
import os
import tempfile


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
class BirdNetClassifyAllTask(luigi.WrapperTask):
    birdclef_root_path = luigi.Parameter()
    output_path = luigi.Parameter()
    n_threads = luigi.IntParameter(default=os.cpu_count())

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


if __name__ == "__main__":
    luigi.build(
        [
            BirdNetClassifyAllTask(
                birdclef_root_path="data/raw/birdclef-2022",
                output_path="data/intermediate/birdclef-2022/birdnet/analyze",
                n_threads=4,
            )
        ],
        log_level="INFO",
        workers=os.cpu_count() // 4,
    )

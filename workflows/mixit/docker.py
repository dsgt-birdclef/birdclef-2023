import os
import shutil
import tempfile
from pathlib import Path

import luigi
from luigi.contrib.docker_runner import DockerTask

from workflows.utils.mixin import DynamicRequiresMixin


class MixitDockerTask(DockerTask, DynamicRequiresMixin):
    """Run Mixit on an audio file."""

    input_path = luigi.Parameter()
    output_path = luigi.Parameter()
    # {species}/{track}.ogg
    track_name = luigi.Parameter()
    num_sources = luigi.IntParameter(default=4)

    image = "us-central1-docker.pkg.dev/birdclef-2023/birdclef-2023/bird-mixit:latest"
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
        return [
            f"{root}:/mnt/data",
            f"{self.staging_path}:/mnt/staging_output",
        ]

    def output(self):
        filename = Path(self.track_name)
        return [
            luigi.LocalTarget(
                f"{self.output_path}/{filename.parent.name}/{filename.stem}_source{i}.mp3"
            )
            for i in range(self.num_sources)
        ]

    @property
    def command(self):
        return " ".join(
            [
                "python scripts/mixit_wrapper.py",
                f"--input /mnt/{self.input_path}/{self.track_name}",
                f"--output /mnt/staging_output/{self.track_name}",
                f"--model_name output_sources{self.num_sources}",
                f"--num_sources {self.num_sources}",
                f"--output_format mp3",
            ]
        )

    def run(self):
        super().run()
        # move the intermediate results to the output, ensuring parents exist
        parent = Path(self.output()[0].path).parent
        parent.mkdir(parents=True, exist_ok=True)
        print(f"Moving {self.staging_path} to {parent}")
        for path in Path(self.staging_path).glob("**/*"):
            if path.is_dir():
                continue
            print(f"Moving {path} to {parent.parent}")
            path.rename(parent.parent / path.parent.name / path.name)
        shutil.rmtree(self.staging_path)

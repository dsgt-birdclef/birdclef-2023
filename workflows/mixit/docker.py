import logging
import os
import shutil
import tempfile
from pathlib import Path

import luigi
import torch
from luigi.contrib.docker_runner import DockerTask

import docker
from workflows.utils.mixin import DynamicRequiresMixin


class MixitDockerTask(DockerTask, DynamicRequiresMixin):
    """Run Mixit on an audio file."""

    resources = {"max_workers": 2} if torch.cuda.is_available() else {}

    input_path = luigi.Parameter()
    output_path = luigi.Parameter()
    # {species}/{track}.ogg
    track_name = luigi.Parameter()
    num_sources = luigi.IntParameter(default=4)

    image = (
        "us-central1-docker.pkg.dev/birdclef-2023/birdclef-2023/{image}:latest".format(
            image="bird-mixit-gpu" if torch.cuda.is_available() else "bird-mixit"
        )
    )
    container_options = {"user": f"{os.getuid()}:{os.getgid()}"}
    host_config_options = (
        {
            "device_requests": [
                docker.types.DeviceRequest(count=1, capabilities=[["gpu"]])
            ]
        }
        if torch.cuda.is_available()
        else {}
    )
    # We don't need this, and cause more issus than it solves
    mount_tmp = False

    @property
    def staging_path(self):
        # a singleton variable that's set on the first call, hacky solution
        if not hasattr(self, "_staging_path"):
            self._staging_path = Path(tempfile.mkdtemp(prefix="docker-mixit-"))
            # chown directory to current user
            os.chown(self._staging_path, os.getuid(), os.getgid())
            # also create the relevant directories from the track name
            path = Path(self.track_name)
            (self._staging_path / path.parent.name).mkdir(parents=True, exist_ok=True)
            return self._staging_path
        else:
            return self._staging_path

    @property
    def binds(self):
        root = Path("./data").absolute()
        path = Path(self.track_name)
        return [
            f"{root}:/mnt/data:ro",
            # NOTE: we mount the specific parent folder that contains the track,
            # otherwise we run into permission issues when writing the output.
            # Why? I don't know...
            f"{self.staging_path}/{path.parent.name}:/mnt/staging_output/{path.parent.name}",
            # NOTE: it can be helpful mount the script into the container
            # f"{Path('./scripts').absolute()}:/app/scripts:ro",
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
        logging.info(f"container options: {self.container_options}")
        logging.info(f"host config options: {self.host_config_options}")
        logging.info(f"binds: {self.binds}")
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


if __name__ == "__main__":
    # test the gpu version of this
    train_audio = "data/raw/birdclef-2023/train_audio"
    species = list(Path(train_audio).glob("**/*.ogg"))
    luigi.build(
        [
            MixitDockerTask(
                input_path=train_audio,
                output_path="data/intermediate/luigi/mixit-test",
                track_name=path.relative_to(train_audio).as_posix(),
                num_sources=4,
            )
            for path in species[:4]
        ],
        workers=4,
        scheduler_host="luigi.us-central1-a.c.birdclef-2023.internal",
        log_level="INFO",
    )

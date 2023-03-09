import numpy as np
import pytest
import soundfile as sf


@pytest.fixture(scope="session")
def bird_species():
    yield ["foo", "bar", "baz"]


@pytest.fixture(scope="session")
def train_root(tmp_path_factory, bird_species):
    tmp_path = tmp_path_factory.mktemp("train")
    sr = 32000
    for i, bird in enumerate(bird_species):
        path = tmp_path / bird
        path.mkdir()
        for j in range(2):
            sf.write(
                path / f"{j}.ogg",
                np.ones(3 * 5 * sr) * i,
                sr,
                format="ogg",
                subtype="vorbis",
            )
    return tmp_path
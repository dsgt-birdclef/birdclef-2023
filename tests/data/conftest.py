from pathlib import Path

import pytest
import tensorflow as tf
from tensorflow import keras


@pytest.fixture(scope="session")
def birdnet_model_path(tmpdir_factory):
    model = keras.Sequential(
        [
            keras.Input(shape=(144_000,)),
            keras.layers.Dense(320, activation="relu"),
            keras.layers.Dense(3337, activation="softmax"),
        ]
    )
    model.build()
    path = Path(tmpdir_factory.mktemp("model"))
    tf.keras.models.save_model(model, path)
    return path

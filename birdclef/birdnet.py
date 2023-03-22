"""
This module contains some utility functions for dealing with the birdnet model.

We write our own wrappers over the raw keras model.
"""
from typing import Optional

from tensorflow import keras


def load_model(path: str, model_attr: Optional[str] = "model") -> keras.Model:
    """
    Load the birdnet model.

    Args:
        path: The path to the model.

    Returns:
        The loaded model.
    """
    # the actual keras model is under the model attribute
    model = keras.models.load_model(path)
    if model_attr:
        model = getattr(model, model_attr)
    return model


def embedding_func(model: keras.Model):
    """
    Create a function that can be used to extract the embedding layer from the model.

    Args:
        model: The model to extract the embedding layer from.

    Returns:
        The function that can be used to extract the embedding layer.
    """
    return keras.backend.function([model.input], [model.layers[-2].output])


def prediction_func(model: keras.Model):
    """
    Create a function that can be used to extract the prediction layer from the model.

    Args:
        model: The model to extract the prediction layer from.

    Returns:
        The function that can be used to extract the prediction layer.
    """
    return keras.backend.function([model.input], [model.layers[-1].output])

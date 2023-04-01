"""
This module contains some utility functions for dealing with the birdnet model.

We write our own wrappers over the raw keras model.
"""
import json
from pathlib import Path
from typing import Optional

import numpy as np
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


def load_model_from_repo(birdnet_root: str) -> keras.Model:
    # load our optimized model
    if (Path(birdnet_root) / "model").exists():
        return load_model(Path(birdnet_root) / "model", model_attr=None)
    else:
        return load_model(
            Path(birdnet_root) / "checkpoints/V2.2/BirdNET_GLOBAL_3K_V2.2_Model/"
        )


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


def load_labels(birdnet_root: str):
    # we rename the labels when copying over the model in the optimized model
    if (Path(birdnet_root) / "model").exists():
        path = Path(birdnet_root) / "labels.txt"
    else:
        path = Path(birdnet_root) / "checkpoints/V2.2/BirdNET_GLOBAL_3K_V2.2_Labels.txt"
    labels = Path(path).read_text().splitlines()
    return labels


def load_mapped_labels(birdnet_root: str):
    path = Path(birdnet_root) / "eBird_taxonomy_codes_2021E.json"
    labels = load_labels(birdnet_root)
    mapping = json.loads(path.read_text())
    mapped_labels = [mapping[label] for label in labels]
    return mapped_labels


def rank_indices(pred, k=10):
    """
    Rank the indices of the predictions.
    """
    topk = np.argsort(pred, axis=1)[:, -k * 2 :]
    values, counts = np.unique(topk, return_counts=True)
    ind = np.argpartition(-counts, kth=k)[:k]
    return values[ind]

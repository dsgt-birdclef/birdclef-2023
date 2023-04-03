import numpy as np
import pytest
import torch

from birdclef import birdnet
from birdclef.data.transforms import (
    ToBirdNETEmbedding,
    ToBirdNETPrediction,
    ToFloatTensor,
)


def test_to_float_tensor():
    arrays = [np.ones(16) for _ in range(3)]
    res = ToFloatTensor()(arrays)
    for item in res:
        assert isinstance(item, torch.Tensor)


def test_to_birdnet_embedding(birdnet_model_path):
    sample_rate = 48_000
    X = np.random.randn(5, sample_rate * 3)
    model = birdnet.load_model(birdnet_model_path, model_attr=None)
    res = ToBirdNETEmbedding(model)(X)
    assert res.shape == (5, 320)


def test_to_birdnet_predictions(birdnet_model_path):
    sample_rate = 48_000
    X = np.random.randn(5, sample_rate * 3)
    model = birdnet.load_model(birdnet_model_path, model_attr=None)
    res = ToBirdNETPrediction(model)(X)
    assert res.shape == (5, 3337)

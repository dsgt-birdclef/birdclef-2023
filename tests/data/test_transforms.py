import numpy as np
import pytest
import torch

from birdclef.data.transforms import ToBirdNETEmbedding, ToFloatTensor


def test_to_float_tensor():
    arrays = [np.ones(16) for _ in range(3)]
    res = ToFloatTensor()(arrays)
    for item in res:
        assert isinstance(item, torch.Tensor)


@pytest.mark.skip(reason="TODO: create a dummy model to test this all the way through")
def test_to_birdnet_embedding():
    # TODO: create a dummy model to test this all the way through
    model_path = None
    sample_rate = 48_000
    X = np.random.randn(sample_rate)
    y = "test"
    res = ToBirdNETEmbedding(model_path)([X, y])
    # TODO: a proper test here
    assert False

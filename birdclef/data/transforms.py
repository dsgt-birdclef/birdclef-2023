import torch
from tensorflow import keras

from birdclef import birdnet


class ToFloatTensor:
    """Converts numpy arrays to float Variables in Pytorch."""

    def __init__(self, device=None):
        self.device = device

    def __call__(self, sample):
        z = [torch.from_numpy(z).float() for z in sample]
        if self.device is not None:
            z = [z.to(self.device) for z in z]
        return tuple(z)


class ToBirdNETEmbedding:
    """Converts the samples into embedding space given a tensorflow keras model."""

    def __init__(self, model):
        self.func = birdnet.embedding_func(model)

    def __call__(self, X):
        return self.func(X)[0]


class ToBirdNETPrediction:
    """Converts the samples into prediction space given a tensorflow keras model."""

    def __init__(self, model):
        self.func = birdnet.prediction_func(model)

    def __call__(self, X):
        return self.func(X)[0]

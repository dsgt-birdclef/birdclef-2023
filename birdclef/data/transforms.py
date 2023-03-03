import torch


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
    """Converts the samples into embedding space."""

    def __init__(self, model_path):
        # TODO: load the model
        self.model = lambda x: x

    def __call__(self, sample):
        X, y = sample
        return self.model(X), y

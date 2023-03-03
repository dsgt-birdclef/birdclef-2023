import numpy as np
import torch
from torch.utils.data import IterableDataset


def get_worker_indices(total_rows):
    """Given a set of discrete rows, return a subset of rows for each worker."""
    # https://pytorch.org/docs/stable/data.html#torch.utils.data.IterableDataset
    worker_info = torch.utils.data.get_worker_info()
    num_workers = 1 if worker_info is None else worker_info.num_workers
    worker_id = 0 if worker_info is None else worker_info.id

    # compute number of rows per worker
    rows_per_worker = int(np.ceil(total_rows / num_workers))
    start = worker_id * rows_per_worker
    end = start + rows_per_worker
    return start, end


class AudioPCMDataSet(IterableDataset):
    """Iterate over a list of files and return the audio data and track name.

    This is effectively a wrapper around librosa functionality. We can use in a data module
    to reshape the data into a form we expect, by passing transforms into this dataset. For
    example, we use a ToBirdNETEmbedding transform to convert the audio data into the
    """

    def __init__(
        self, path, valid_ext=["ogg", "mp3"], sample_rate=48_000, transform=None
    ):
        super().__init__()
        self.sample_rate = sample_rate
        self.path = path
        self.valid_ext = valid_ext

    def _get_paths(self, path, valid_ext):
        """Return a list of all paths under the current path that match the valid extensions."""
        raise NotImplementedError

    def _items(self, paths):
        """Iterate of a list of files, returning the relevant audio data for each track."""
        # TODO: implement something reasonable here
        # as a placehold, we're going to generate noise in the correct shape
        for path in paths:
            data = np.random.randn(1, self.sample_rate)
            # TODO: we want to return a number as the label, not a string. It'd be a good idea to
            # perhaps hash the species/audio name to get a unique integer for each track. This way
            # when we're batching down the line, we can rely on the label as an identifier. It's
            # also reasonable to batch in the dataset, but we might have to pre-process the audio files
            # to cut them into deterministic chunks.
            yield data, path.stem

    def __iter__(self):
        paths = self._get_paths(self.path, self.valid_ext)
        start, end = get_worker_indices(len(paths))
        for item in self._items(paths[start:end]):
            yield item

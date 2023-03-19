from pathlib import Path

import librosa
import numpy as np
import torch
from torch.utils.data import IterableDataset

from .utils import slice_seconds


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
        self,
        path,
        valid_ext=["ogg", "mp3"],
        sample_rate=48_000,
        transform=None,
        min_duration=10,
        window_step=1,
    ):
        super().__init__()
        self.sample_rate = sample_rate
        self.path = Path(path)
        self.valid_ext = valid_ext
        self.min_duration = min_duration
        self.window_step = window_step

    def _get_paths(self, path, valid_ext):
        """Return a list of all paths under the current path that match the valid extensions."""
        return [p for p in path.glob(f"**/*") if p.suffix[1:] in valid_ext]

    def _items(self, paths):
        """Iterate of a list of files, returning the relevant audio data for each track."""
        for path in paths:
            y, sr = librosa.load(path, sr=self.sample_rate)
            # only keep the data that reaches the minimum threshold

            # get the number of seconds
            seconds = librosa.get_duration(y=y, sr=sr)
            if seconds < self.min_duration:
                continue

            # return a sequence of 3 second chunks with a 1 second sliding
            # window. this means there will be significant overlap between
            # chunks, but we can accept this for now.
            sliced = slice_seconds(y, sr, seconds=3, step=self.window_step)
            assert (
                sliced[0].shape[0] == sr * 3
            ), f"first slice is not 3 seconds, {sliced[0]}"
            # now yield min_duration chunks of data
            # we want consequenctive sequences to have at least 50% differences
            print(len(sliced), len(sliced[0]), print(sliced))
            step = self.min_duration // 2
            for start in range(0, int(seconds), step):
                # only keep as many chunks that we can fit in the min duration
                end = start + (self.min_duration // self.window_step)
                if end > seconds:
                    break
                # get the data for this chunk
                data = sliced[start:end]
                print(data.shape)
                yield data

    def __iter__(self):
        paths = self._get_paths(self.path, self.valid_ext)
        start, end = get_worker_indices(len(paths))
        for item in self._items(paths[start:end]):
            yield item

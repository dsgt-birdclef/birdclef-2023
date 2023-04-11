import librosa
import numpy as np
import torch


def slice_seconds(data, sample_rate, seconds=3, pad_seconds=0, step=None):
    # compute step size
    k = sample_rate * seconds
    pad = sample_rate * pad_seconds
    step = k + pad if step is None else int(sample_rate * step)

    remainder = len(data) % step
    # right pad the data with zeros to make it evenly divisible
    if remainder:
        padding_size = step - remainder
        data = np.pad(data, (0, padding_size))

    n = len(data)
    indices = [np.arange(i, i + k + pad) for i in range(0, n, step) if i + k + pad <= n]
    indexed = np.stack([data[i] for i in indices])
    if indexed.shape[0] == 0:
        return []
    return indexed


def slice_seconds_indexed(data, sample_rate, seconds=3, pad_seconds=0, step=None):
    indexed = slice_seconds(data, sample_rate, seconds, pad_seconds, step)
    time_index = np.arange(indexed.shape[0] + 1) * seconds
    return list(zip(time_index, indexed))

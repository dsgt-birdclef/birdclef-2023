import numpy as np

from birdclef.data.utils import slice_seconds


def test_slice_seconds_right_pad():
    x = np.ones(16)
    res = slice_seconds(x, 1, 5)
    assert len(res) == 4

    # assert 1st slice is correct
    i, v = res[0]
    assert i == 0
    assert (v - np.ones(5)).sum() == 0

    # assert last slice is right-padded correctly
    i, v = res[3]
    assert i == 15
    assert (v - np.array([1, 0, 0, 0, 0])).sum() == 0


def test_slice_seconds_step_size():
    x = np.arange(16)
    res = slice_seconds(x, 1, 4, step=2)
    print(res)
    assert len(res) == 7

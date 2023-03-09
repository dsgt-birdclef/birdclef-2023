from birdclef.data.datasets import AudioPCMDataSet


def test_dataset_loads_audio(train_root):
    sample_rate = 48_000
    ds = AudioPCMDataSet(train_root, sample_rate=sample_rate)

    # TODO: write some tests here
    assert False

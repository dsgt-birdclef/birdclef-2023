import pytest

from birdclef.data.datasets import AudioPCMDataSet


@pytest.mark.parametrize(
    "duration,step",
    [(10, 1), (10, 3), (7, 5)],
)
def test_audio_pcm_dataset_loads_audio(train_audio, duration, step):
    sample_rate = 48_000
    ds = AudioPCMDataSet(
        train_audio, sample_rate=sample_rate, min_duration=duration, window_step=step
    )

    row = next(iter(ds))
    assert row.shape == (duration // step, sample_rate * 3), "dimensions are incorrect"

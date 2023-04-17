import pytest
from tensorflow import keras

from birdclef.data.datasets import AudioPCMDataSet
from birdclef.data.transforms import ToBirdNETEmbedding


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


def test_train_audio_dataset_with_transforms(train_audio, birdnet_model_path):
    sample_rate = 48_000
    ds = AudioPCMDataSet(
        train_audio,
        sample_rate=sample_rate,
        min_duration=10,
        window_step=1,
        transforms=[
            ToBirdNETEmbedding(keras.models.load_model(birdnet_model_path)),
        ],
    )

    row = next(iter(ds))
    print(row)
    assert row.shape == (10, 320), "dimensions are incorrect"

import os
import shutil
from pathlib import Path

import numpy as np
import pytest
import torch
from sklearn.model_selection import train_test_split

from birdclef.birdnet import load_model
from birdclef.data.datasets import AudioPCMDataSet
from birdclef.data.transforms import ToBirdNETEmbedding
from birdclef.transformer import TransformerModel, create_mask, split_and_copy_files


def test_create_mask():
    embeddings = torch.rand(32, 320)
    mask = create_mask(embeddings)
    assert mask.size() == embeddings.size()
    assert torch.sum(mask).item() > 0


def test_TransformerModel():
    input_dim = 320
    model_dim = 256
    num_heads = 8
    num_layers = 4
    model = TransformerModel(input_dim, model_dim, num_heads, num_layers)

    x = torch.rand(32, 320)
    y = model(x)

    assert y.size() == x.size()


def test_split_and_copy_files(tmp_path):
    parent_dir = Path(__file__).parent.parent
    source_dir = parent_dir / "data/raw/birdclef-2022/train_audio/mp3/"
    train_ratio = 0.8
    val_ratio = 0.1

    # Create a temporary folder for testing purposes
    dest_dir = tmp_path / "data"
    dest_dir.mkdir()
    for folder in source_dir.glob("*"):
        (dest_dir / folder.name).mkdir()
        for file in folder.glob("*.mp3"):
            (dest_dir / folder.name / file.name).write_bytes(file.read_bytes())

    train_dir, val_dir, test_dir = split_and_copy_files(
        dest_dir, train_ratio, val_ratio
    )

    assert train_dir.exists()
    assert val_dir.exists()
    assert test_dir.exists()

    for subfolder in dest_dir.glob("*"):
        if subfolder.is_dir():
            train_files = list((train_dir / subfolder.name).glob("*.mp3"))
            val_files = list((val_dir / subfolder.name).glob("*.mp3"))
            test_files = list((test_dir / subfolder.name).glob("*.mp3"))

            total_files = len(train_files) + len(val_files) + len(test_files)
            orig_files = len(list(subfolder.glob("*.mp3")))

            assert total_files == orig_files

    shutil.rmtree(dest_dir)  # Cleanup temporary folder after testing

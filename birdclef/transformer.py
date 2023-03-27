from pathlib import Path

import pytorch_lightning as pl
import tensorflow as tf
import torch
import torch.nn as nn
import torch.nn.functional as F
from tensorflow import keras
from torch.utils.data import DataLoader

from birdclef.birdnet import load_model
from birdclef.data.datasets import AudioPCMDataSet
from birdclef.data.transforms import ToBirdNETEmbedding


class TransformerModel(pl.LightningModule):
    def __init__(
        self,
        input_dim,
        model_dim,
        num_heads,
        num_layers,
        num_classes,
        lr=1e-3,
    ):
        super().__init__()
        self.lr = lr
        self.transformer = nn.Transformer(
            model_dim,
            num_heads,
            num_layers,
            dropout=0.1,
            batch_first=True,
        )
        self.fc = nn.Linear(model_dim, num_classes)

    def forward(self, x):
        x = self.transformer(x)
        x = self.fc(x)
        return x

    def l2_loss(self, pred, target):
        return torch.mean((pred - target) ** 2)

    def training_step(self, batch, batch_idx):
        x, y = batch
        y_pred = self(x)
        loss = self.l2_loss(y_pred[:, :-1, :], y[:, 1:, :])
        self.log("train_loss", loss, on_step=True, on_epoch=True)
        return loss

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.lr)
        return optimizer


def main():
    # Define the dataset and DataLoader
    parent_dir = Path(__file__).parent.parent
    train_audio = parent_dir / "data/raw/birdclef-2022/train_audio/mp3/"
    birdnet_model_path = (
        parent_dir
        / "vendor/BirdNET-Analyzer/checkpoints/V2.2/BirdNET_GLOBAL_3K_V2.2_Model/"
    )

    sample_rate = 48_000

    birdnet_model = load_model(birdnet_model_path)
    print(birdnet_model.summary())

    # Load the full dataset
    full_dataset = AudioPCMDataSet(
        train_audio,
        sample_rate=sample_rate,
        min_duration=10,
        window_step=1,
        transforms=[
            ToBirdNETEmbedding(birdnet_model),
        ],
    )

    # Split the full dataset into train and validation sets
    # train_size = int(0.8 * len(full_dataset))
    # val_size = len(full_dataset) - train_size
    # train_dataset, val_dataset = torch.utils.data.random_split(full_dataset, [train_size, val_size])

    # Create DataLoaders for train and validation sets
    train_dataloader = DataLoader(full_dataset, batch_size=32, num_workers=4)
    # val_dataloader = DataLoader(val_dataset, batch_size=32, num_workers=4)

    # Define the model
    model = TransformerModel(
        input_dim=80,
        model_dim=256,
        num_heads=8,
        num_layers=4,
        num_classes=80,
    )

    # Train the model
    trainer = pl.Trainer(accelerator="auto")
    trainer.fit(model, train_dataloader)


if __name__ == "__main__":
    main()

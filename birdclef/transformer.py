from pathlib import Path

import numpy as np
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


def create_mask(embeddings, mask_prob=0.15):
    mask = np.random.rand(*embeddings.shape) < mask_prob
    mask = torch.tensor(mask, dtype=torch.bool)
    return mask


class TransformerModel(pl.LightningModule):
    def __init__(
        self,
        input_dim,
        model_dim,
        num_heads,
        num_layers,
        lr=1e-3,
    ):
        super().__init__()
        self.lr = lr
        self.input_fc = nn.Linear(input_dim, model_dim)
        self.transformer = nn.Transformer(
            model_dim,
            nhead=num_heads,
            num_encoder_layers=num_layers,
            num_decoder_layers=num_layers,
            dropout=0.1,
        )
        self.output_fc = nn.Linear(model_dim, input_dim)

    def forward(self, x):
        x = self.input_fc(x)
        x = self.transformer(x, x)
        x = self.output_fc(x)
        return x

    def masked_loss(self, pred, target, mask):
        loss = (pred - target) ** 2
        masked_loss = loss[mask]
        return torch.mean(masked_loss)

    def training_step(self, batch, batch_idx):
        x, y, mask = batch
        y_pred = self(x)
        loss = self.masked_loss(y_pred, y, mask)
        acc = self.masked_accuracy(y_pred, y, mask)  # Calculate accuracy
        self.log("train_loss", loss, on_step=True, on_epoch=True)
        self.log("train_acc", acc, on_step=True, on_epoch=True)  # Log accuracy
        return loss

    def validation_step(self, batch, batch_idx):
        x, y, mask = batch
        y_pred = self(x)
        loss = self.masked_loss(y_pred, y, mask)
        acc = self.masked_accuracy(y_pred, y, mask)  # Calculate accuracy
        self.log("val_loss", loss, on_step=True, on_epoch=True)
        self.log("val_acc", acc, on_step=True, on_epoch=True)  # Log accuracy
        return loss

    def masked_accuracy(self, pred, target, mask):
        correct = (torch.argmax(pred, dim=-1) == torch.argmax(target, dim=-1)).float()
        masked_correct = correct[mask]
        return torch.mean(masked_correct)

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

    # Split the dataset into train, validation, and test sets
    train_size = int(0.8 * len(full_dataset))
    val_size = int(0.1 * len(full_dataset))
    test_size = len(full_dataset) - train_size - val_size
    train_dataset, val_dataset, test_dataset = random_split(
        full_dataset, [train_size, val_size, test_size]
    )

    # Define the model
    model = TransformerModel(
        input_dim=320,
        model_dim=256,
        num_heads=8,
        num_layers=4,
    )

    # Create DataLoader and apply masks
    def collate_fn(batch):
        batch = [torch.from_numpy(item) for item in batch]
        embeddings = torch.cat(batch, dim=0)
        masks = create_mask(embeddings)
        masked_embeddings = embeddings.clone().detach()
        masked_embeddings[masks] = 0
        return masked_embeddings, embeddings, masks

    train_dataloader = DataLoader(
        train_dataset, batch_size=32, num_workers=0, collate_fn=collate_fn
    )
    val_dataloader = DataLoader(
        val_dataset, batch_size=32, num_workers=0, collate_fn=collate_fn
    )
    test_dataloader = DataLoader(
        test_dataset, batch_size=32, num_workers=0, collate_fn=collate_fn
    )

    # Train the model

    # Train the model
    trainer = pl.Trainer(accelerator="cpu", default_root_dir="data/lightning_logs")
    trainer.fit(model, train_dataloader, val_dataloader)

    # Evaluate the model on the test set
    trainer.test(model, test_dataloader)


if __name__ == "__main__":
    main()

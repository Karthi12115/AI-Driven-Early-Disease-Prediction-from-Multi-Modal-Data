"""Training entry points and synthetic smoke-test training."""

from __future__ import annotations

from pathlib import Path

import torch
from torch import nn
from torch.optim import Adam

from src.models.multimodal_model import MultimodalRiskModel
from src.utils.io_utils import load_config, resolve_path
from src.utils.seed_utils import set_global_seed


def build_model(config: dict) -> MultimodalRiskModel:
    return MultimodalRiskModel(config)


def create_demo_batch(config: dict, batch_size: int = 4) -> tuple[dict, torch.Tensor]:
    model_cfg = config["model"]
    preprocessing_cfg = config["preprocessing"]
    labels = torch.randint(0, 2, (batch_size, len(model_cfg["outcomes"]))).float()
    genomics_mask = torch.ones(batch_size, dtype=torch.bool)
    image_mask = torch.ones(batch_size, dtype=torch.bool)
    if batch_size > 1:
        genomics_mask[1] = False
    if batch_size > 2:
        image_mask[2] = False
    batch = {
        "ehr": torch.randn(batch_size, int(model_cfg["ehr_input_dim"])),
        "genomics": torch.randn(batch_size, int(model_cfg["genomics_input_dim"])),
        "wearable": torch.randn(
            batch_size,
            int(preprocessing_cfg["wearable_sequence_length"]),
            int(model_cfg["wearable_input_dim"]),
        ),
        "image": torch.randn(batch_size, int(model_cfg["image_channels"]), 64, 64),
        "text": torch.randint(
            0,
            int(model_cfg["text_vocab_size"]),
            (batch_size, int(model_cfg["text_sequence_length"])),
        ),
        "modality_mask": {
            "ehr": torch.ones(batch_size, dtype=torch.bool),
            "genomics": genomics_mask,
            "wearable": torch.ones(batch_size, dtype=torch.bool),
            "image": image_mask,
            "text": torch.ones(batch_size, dtype=torch.bool),
        },
    }
    return batch, labels


def train_demo(config_path: str = "config/config.yaml", output_path: str = "artifacts/models/demo_model.pt") -> Path:
    config = load_config(config_path)
    set_global_seed(int(config["project"]["seed"]))
    model = build_model(config)
    model.train()

    batch, labels = create_demo_batch(config)
    optimizer = Adam(model.parameters(), lr=float(config["training"]["learning_rate"]))
    criterion = nn.BCEWithLogitsLoss()

    for _ in range(2):
        optimizer.zero_grad()
        output = model(batch)
        loss = criterion(output["logits"], labels)
        loss.backward()
        optimizer.step()

    resolved = resolve_path(output_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model_state": model.state_dict(), "config": config}, resolved)
    return resolved

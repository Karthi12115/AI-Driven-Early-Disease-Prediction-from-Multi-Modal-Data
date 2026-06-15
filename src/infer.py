"""Inference helpers."""

from __future__ import annotations

from pathlib import Path

import torch

from src.explainability.modality_attention import summarize_attention
from src.models.multimodal_model import MultimodalRiskModel
from src.train import create_demo_batch
from src.utils.io_utils import load_config, load_json, resolve_path


def load_preprocessing_assets(config: dict | None = None) -> dict[str, dict]:
    """Load fitted scalers, tokenizers, and label mappings saved as JSON."""

    active_config = config or load_config()
    artifact_paths = active_config["paths"]["artifacts"]
    assets: dict[str, dict] = {}
    for group in ("scalers", "tokenizers", "label_mappings"):
        root = resolve_path(artifact_paths[group])
        assets[group] = {}
        if root.exists():
            for path in root.glob("*.json"):
                assets[group][path.stem] = load_json(path)
    return assets


def load_model(checkpoint_path: str | Path, config: dict | None = None) -> MultimodalRiskModel:
    checkpoint = torch.load(resolve_path(checkpoint_path), map_location="cpu")
    model_config = config or checkpoint.get("config") or load_config()
    model = MultimodalRiskModel(model_config)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    return model


def predict_batch(model: MultimodalRiskModel, batch: dict) -> dict:
    with torch.no_grad():
        output = model(batch)
    probabilities = output["probabilities"].detach().cpu().tolist()
    return {
        "outcomes": model.outcomes,
        "probabilities": probabilities,
        "attention": summarize_attention(output["attention"]),
    }


def infer_demo(checkpoint_path: str = "artifacts/models/demo_model.pt") -> dict:
    config = load_config()
    model = load_model(checkpoint_path, config)
    batch, _ = create_demo_batch(config, batch_size=1)
    return predict_batch(model, batch)

"""End-to-end multimodal risk model."""

from __future__ import annotations

import torch
from torch import nn

from src.models.ehr_encoder import EHREncoder
from src.models.fusion_attention import AttentionFusion
from src.models.genomics_encoder import GenomicsEncoder
from src.models.image_encoder import ImageEncoder
from src.models.predictor import Predictor
from src.models.text_encoder import TextEncoder
from src.models.wearable_encoder import WearableEncoder


class MultimodalRiskModel(nn.Module):
    def __init__(self, config: dict) -> None:
        super().__init__()
        model_cfg = config["model"]
        modality_cfg = config.get("modalities", {})
        embedding_dim = int(model_cfg["embedding_dim"])
        dropout = float(model_cfg.get("dropout", 0.2))

        self.outcomes = list(model_cfg["outcomes"])
        self.modalities = [name for name, enabled in modality_cfg.items() if enabled]
        self.encoders = nn.ModuleDict()

        if "ehr" in self.modalities:
            self.encoders["ehr"] = EHREncoder(int(model_cfg["ehr_input_dim"]), embedding_dim, dropout)
        if "genomics" in self.modalities:
            self.encoders["genomics"] = GenomicsEncoder(int(model_cfg["genomics_input_dim"]), embedding_dim, dropout)
        if "wearable" in self.modalities:
            self.encoders["wearable"] = WearableEncoder(
                int(model_cfg["wearable_input_dim"]),
                int(model_cfg["wearable_hidden_dim"]),
                embedding_dim,
                dropout,
            )
        if "image" in self.modalities:
            self.encoders["image"] = ImageEncoder(int(model_cfg["image_channels"]), embedding_dim, dropout)
        if "text" in self.modalities:
            self.encoders["text"] = TextEncoder(int(model_cfg["text_vocab_size"]), embedding_dim, dropout)

        self.fusion = AttentionFusion(embedding_dim, self.modalities)
        self.predictor = Predictor(embedding_dim, len(self.outcomes), dropout)

    def forward(self, batch: dict[str, torch.Tensor | dict[str, torch.Tensor]]) -> dict[str, object]:
        features = {}
        for modality, encoder in self.encoders.items():
            if modality in batch:
                features[modality] = encoder(batch[modality])

        mask = batch.get("modality_mask")
        fused, attention = self.fusion(features, mask if isinstance(mask, dict) else None)
        logits = self.predictor(fused)
        probabilities = torch.sigmoid(logits)
        return {
            "logits": logits,
            "probabilities": probabilities,
            "attention": attention,
        }

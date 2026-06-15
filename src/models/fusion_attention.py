"""Attention-based late fusion for modality embeddings."""

from __future__ import annotations

import torch
from torch import nn


class AttentionFusion(nn.Module):
    def __init__(self, embedding_dim: int, modalities: list[str]) -> None:
        super().__init__()
        self.modalities = list(modalities)
        self.scorer = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim // 2),
            nn.Tanh(),
            nn.Linear(embedding_dim // 2, 1),
        )

    def forward(
        self,
        features: dict[str, torch.Tensor],
        modality_mask: dict[str, torch.Tensor] | None = None,
    ) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
        available = [modality for modality in self.modalities if modality in features]
        if not available:
            raise ValueError("At least one modality feature tensor is required")

        stacked = torch.stack([features[modality] for modality in available], dim=1)
        scores = self.scorer(stacked).squeeze(-1)

        if modality_mask is not None:
            mask = torch.stack(
                [
                    modality_mask.get(
                        modality,
                        torch.ones(stacked.size(0), dtype=torch.bool, device=stacked.device),
                    ).to(stacked.device).bool()
                    for modality in available
                ],
                dim=1,
            )
            all_missing = ~mask.any(dim=1)
            if all_missing.any():
                mask[all_missing, 0] = True
            scores = scores.masked_fill(~mask, torch.finfo(scores.dtype).min)

        weights = torch.softmax(scores, dim=1)
        fused = (stacked * weights.unsqueeze(-1)).sum(dim=1)
        attention = {modality: weights[:, index] for index, modality in enumerate(available)}
        return fused, attention

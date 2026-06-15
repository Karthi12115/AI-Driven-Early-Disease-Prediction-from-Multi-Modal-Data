"""Risk prediction head."""

from __future__ import annotations

import torch
from torch import nn


class Predictor(nn.Module):
    def __init__(self, embedding_dim: int, output_dim: int, dropout: float = 0.2) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(embedding_dim, output_dim),
        )

    def forward(self, fused: torch.Tensor) -> torch.Tensor:
        return self.network(fused)

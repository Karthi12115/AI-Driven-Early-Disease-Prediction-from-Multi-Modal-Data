"""EHR tabular encoder."""

from __future__ import annotations

import torch
from torch import nn


class EHREncoder(nn.Module):
    def __init__(self, input_dim: int, embedding_dim: int, dropout: float = 0.2) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, embedding_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(embedding_dim, embedding_dim),
            nn.ReLU(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x.float())

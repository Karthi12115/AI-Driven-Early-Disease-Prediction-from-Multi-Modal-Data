"""Clinical text encoder."""

from __future__ import annotations

import torch
from torch import nn


class TextEncoder(nn.Module):
    """A lightweight embedding encoder.

    This can be replaced by a Hugging Face transformer while keeping the same
    output contract: one embedding vector per patient note.
    """

    def __init__(self, vocab_size: int, embedding_dim: int, dropout: float = 0.2) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.projection = nn.Sequential(
            nn.LayerNorm(embedding_dim),
            nn.Dropout(dropout),
            nn.Linear(embedding_dim, embedding_dim),
            nn.ReLU(),
        )

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(token_ids.long())
        mask = (token_ids != 0).float().unsqueeze(-1)
        summed = (embedded * mask).sum(dim=1)
        counts = mask.sum(dim=1).clamp_min(1.0)
        return self.projection(summed / counts)

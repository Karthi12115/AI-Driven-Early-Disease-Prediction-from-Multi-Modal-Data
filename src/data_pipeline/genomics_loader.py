"""Load genomic features or precomputed genomic embeddings."""

from __future__ import annotations

from pathlib import Path


def load_genomics_table(path: str | Path) -> list[dict]:
    import pandas as pd

    return pd.read_csv(path).to_dict(orient="records")


def normalize_genomic_vector(vector: list[float], eps: float = 1e-8) -> list[float]:
    if not vector:
        return []
    mean = sum(vector) / len(vector)
    variance = sum((value - mean) ** 2 for value in vector) / len(vector)
    std = variance**0.5
    return [(value - mean) / (std + eps) for value in vector]

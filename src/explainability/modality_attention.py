"""Utilities for converting model attention tensors into readable summaries."""

from __future__ import annotations


def summarize_attention(attention: dict) -> dict[str, float | list[float]]:
    summary: dict[str, float | list[float]] = {}
    for modality, values in attention.items():
        if hasattr(values, "detach"):
            detached = values.detach().cpu()
            if detached.ndim == 0:
                summary[modality] = float(detached.item())
            else:
                as_list = detached.tolist()
                summary[modality] = float(as_list[0]) if len(as_list) == 1 else [float(v) for v in as_list]
        else:
            summary[modality] = float(values)
    return summary


def top_modalities(attention_summary: dict[str, float], top_k: int = 3) -> list[tuple[str, float]]:
    return sorted(attention_summary.items(), key=lambda item: item[1], reverse=True)[:top_k]

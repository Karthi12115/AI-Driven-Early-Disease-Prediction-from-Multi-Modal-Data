"""Attention summaries for available and missing modalities."""

from __future__ import annotations

from typing import Any


DISPLAY_NAMES = {
    "ehr": "EHR",
    "genomics": "Genomics",
    "wearable": "Wearable",
    "image": "Image / Report",
}


def format_attention(weights: dict[str, float]) -> dict[str, float]:
    return {DISPLAY_NAMES.get(name, name.title()): round(float(value), 3) for name, value in weights.items()}


def dominant_modality(weights: dict[str, float]) -> dict[str, Any]:
    if not weights:
        return {"name": "No modality", "weight": 0.0}
    name, weight = max(weights.items(), key=lambda item: item[1])
    return {"name": DISPLAY_NAMES.get(name, name.title()), "weight": round(float(weight), 3)}


"""Preprocessing helpers for tabular, sequence, image, and text inputs."""

from __future__ import annotations

import math
import re
from statistics import median
from typing import Iterable


DEFAULT_MODALITIES = ("ehr", "genomics", "wearable", "image", "text")


def is_missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def impute_tabular(
    records: Iterable[dict],
    numeric_fields: Iterable[str],
    categorical_fields: Iterable[str],
    fill_values: dict[str, object] | None = None,
) -> tuple[list[dict], dict[str, object]]:
    rows = [dict(record) for record in records]
    fill_values = dict(fill_values or {})

    for field in numeric_fields:
        if field not in fill_values:
            values = [float(row[field]) for row in rows if not is_missing(row.get(field))]
            fill_values[field] = median(values) if values else 0.0

    for field in categorical_fields:
        fill_values.setdefault(field, "unknown")

    imputed = []
    for row in rows:
        clean = dict(row)
        for field, fill_value in fill_values.items():
            if is_missing(clean.get(field)):
                clean[field] = fill_value
        imputed.append(clean)
    return imputed, fill_values


def normalize_numeric(
    records: Iterable[dict],
    numeric_fields: Iterable[str],
    stats: dict[str, dict[str, float]] | None = None,
    eps: float = 1e-8,
) -> tuple[list[dict], dict[str, dict[str, float]]]:
    rows = [dict(record) for record in records]
    stats = dict(stats or {})

    for field in numeric_fields:
        if field not in stats:
            values = [float(row[field]) for row in rows if not is_missing(row.get(field))]
            mean = sum(values) / len(values) if values else 0.0
            variance = sum((value - mean) ** 2 for value in values) / len(values) if values else 0.0
            stats[field] = {"mean": mean, "std": variance**0.5}

    normalized = []
    for row in rows:
        clean = dict(row)
        for field in numeric_fields:
            value = 0.0 if is_missing(clean.get(field)) else float(clean[field])
            clean[field] = (value - stats[field]["mean"]) / (stats[field]["std"] + eps)
        normalized.append(clean)
    return normalized, stats


def encode_categorical(
    records: Iterable[dict],
    categorical_fields: Iterable[str],
    mappings: dict[str, dict[str, int]] | None = None,
) -> tuple[list[dict], dict[str, dict[str, int]]]:
    rows = [dict(record) for record in records]
    mappings = dict(mappings or {})

    for field in categorical_fields:
        if field not in mappings:
            values = sorted({str(row.get(field, "unknown")) for row in rows})
            mappings[field] = {value: index for index, value in enumerate(values)}

    encoded = []
    for row in rows:
        clean = dict(row)
        for field in categorical_fields:
            value = str(clean.get(field, "unknown"))
            clean[field] = mappings[field].get(value, mappings[field].setdefault("unknown", len(mappings[field])))
        encoded.append(clean)
    return encoded, mappings


def pad_or_truncate_sequence(
    sequence: list[list[float]] | list[float],
    target_length: int,
    pad_value: float = 0.0,
) -> list:
    if target_length <= 0:
        raise ValueError("target_length must be positive")
    if len(sequence) >= target_length:
        return sequence[:target_length]

    if sequence and isinstance(sequence[0], list):
        width = len(sequence[0])
        pad_item = [pad_value] * width
    else:
        pad_item = pad_value
    return list(sequence) + [pad_item for _ in range(target_length - len(sequence))]


def resample_sequence(sequence: list, target_length: int) -> list:
    if target_length <= 0:
        raise ValueError("target_length must be positive")
    if not sequence:
        return []
    if len(sequence) == target_length:
        return list(sequence)
    if target_length == 1:
        return [sequence[0]]

    result = []
    last_index = len(sequence) - 1
    for index in range(target_length):
        source_index = round(index * last_index / (target_length - 1))
        result.append(sequence[source_index])
    return result


def tokenize_text(
    text: str,
    vocab: dict[str, int] | None = None,
    max_length: int = 128,
) -> tuple[list[int], dict[str, int]]:
    vocab = dict(vocab or {"<pad>": 0, "<unk>": 1})
    tokens = re.findall(r"[A-Za-z0-9_]+", text.lower())
    ids: list[int] = []
    for token in tokens[:max_length]:
        if token not in vocab:
            vocab[token] = len(vocab)
        ids.append(vocab.get(token, vocab["<unk>"]))
    ids = ids + [vocab["<pad>"]] * (max_length - len(ids))
    return ids, vocab


def resize_image_array(image, size: int = 224):
    """Resize an image array while keeping image dependencies optional."""

    from PIL import Image
    import numpy as np

    resized = Image.fromarray(image).resize((size, size))
    return np.asarray(resized)


def modality_mask_from_record(
    record: dict,
    modalities: Iterable[str] = DEFAULT_MODALITIES,
) -> dict[str, bool]:
    return {modality: not is_missing(record.get(modality)) for modality in modalities}

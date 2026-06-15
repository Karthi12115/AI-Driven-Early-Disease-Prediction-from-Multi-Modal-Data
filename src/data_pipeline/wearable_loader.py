"""Load wearable sensor sequences."""

from __future__ import annotations

from pathlib import Path


def load_wearable_csv(path: str | Path) -> list[dict]:
    import pandas as pd

    return pd.read_csv(path).to_dict(orient="records")


def group_sequence_by_patient(
    rows: list[dict],
    patient_id_field: str = "patient_id",
    feature_fields: list[str] | None = None,
) -> dict[str, list[list[float]]]:
    if not rows:
        return {}
    if feature_fields is None:
        feature_fields = [key for key in rows[0].keys() if key != patient_id_field]

    grouped: dict[str, list[list[float]]] = {}
    for row in rows:
        patient_id = str(row[patient_id_field])
        grouped.setdefault(patient_id, []).append([float(row[field]) for field in feature_fields])
    return grouped

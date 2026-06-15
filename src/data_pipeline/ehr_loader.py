"""Load structured EHR data."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


def load_ehr_records(path: str | Path) -> list[dict]:
    """Read EHR records from a CSV file into dictionaries."""

    import pandas as pd

    return pd.read_csv(path).to_dict(orient="records")


def select_ehr_fields(
    records: Iterable[dict],
    numeric_fields: Iterable[str],
    categorical_fields: Iterable[str],
) -> list[dict]:
    selected = []
    fields = list(numeric_fields) + list(categorical_fields)
    for record in records:
        selected.append({field: record.get(field) for field in fields})
    return selected

"""Evaluation command helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils.io_utils import save_json
from src.utils.metrics import multilabel_metrics


def evaluate_prediction_files(
    predictions_path: str | Path,
    labels_path: str | Path,
    output_path: str | Path = "reports/tables/evaluation_metrics.json",
) -> dict:
    predictions = pd.read_csv(predictions_path)
    labels = pd.read_csv(labels_path)
    metrics = multilabel_metrics(labels.values, predictions.values)
    save_json(metrics, output_path)
    return metrics

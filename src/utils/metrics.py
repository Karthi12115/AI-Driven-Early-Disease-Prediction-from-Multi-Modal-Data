"""Metrics for classification and risk-score evaluation."""

from __future__ import annotations

from typing import Any


def _as_lists(values: Any) -> list[list[float]]:
    if hasattr(values, "tolist"):
        values = values.tolist()
    if not values:
        return []
    if isinstance(values[0], (int, float, bool)):
        return [[float(v)] for v in values]
    return [[float(item) for item in row] for row in values]


def multilabel_metrics(
    y_true: Any,
    y_score: Any,
    threshold: float = 0.5,
) -> dict[str, float | None]:
    """Compute common metrics with a scikit-learn path and a small fallback."""

    try:
        from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score

        import numpy as np

        score_array = np.asarray(y_score)
        y_pred = (score_array >= threshold).astype(int)
        output: dict[str, float | None] = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision_micro": float(precision_score(y_true, y_pred, average="micro", zero_division=0)),
            "recall_micro": float(recall_score(y_true, y_pred, average="micro", zero_division=0)),
            "f1_micro": float(f1_score(y_true, y_pred, average="micro", zero_division=0)),
        }
        try:
            output["auc_macro"] = float(roc_auc_score(y_true, y_score, average="macro"))
        except ValueError:
            output["auc_macro"] = None
        return output
    except ImportError:
        pass

    true_rows = _as_lists(y_true)
    score_rows = _as_lists(y_score)
    pred_rows = [[1.0 if value >= threshold else 0.0 for value in row] for row in score_rows]

    total = 0
    exact = 0
    tp = fp = fn = 0
    for true_row, pred_row in zip(true_rows, pred_rows):
        total += 1
        if true_row == pred_row:
            exact += 1
        for truth, pred in zip(true_row, pred_row):
            if truth == 1 and pred == 1:
                tp += 1
            elif truth == 0 and pred == 1:
                fp += 1
            elif truth == 1 and pred == 0:
                fn += 1

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "accuracy": exact / total if total else 0.0,
        "precision_micro": precision,
        "recall_micro": recall,
        "f1_micro": f1,
        "auc_macro": None,
    }

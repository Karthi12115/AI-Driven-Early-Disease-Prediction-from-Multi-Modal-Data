"""Feature importance helpers for tabular review outputs."""

from __future__ import annotations


def rank_feature_importance(
    feature_names: list[str],
    importances: list[float],
    top_k: int = 10,
) -> list[tuple[str, float]]:
    pairs = zip(feature_names, importances)
    return sorted(pairs, key=lambda item: abs(item[1]), reverse=True)[:top_k]

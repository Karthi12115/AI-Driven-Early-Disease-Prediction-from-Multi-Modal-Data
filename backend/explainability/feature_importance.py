"""Feature-level explanations for EHR fields."""

from __future__ import annotations

from typing import Any

from backend.data_pipeline.preprocessing import clamp


def ehr_feature_importance(ehr: dict[str, Any]) -> list[dict[str, Any]]:
    features = ehr.get("features", {})
    history = str(features.get("Medical history", "")).lower()

    contributions = [
        {
            "feature": "Age",
            "impact": clamp((float(features.get("Age", 45.0)) - 35.0) / 65.0),
            "direction": "Higher age increases baseline clinical risk.",
        },
        {
            "feature": "Blood pressure",
            "impact": clamp((float(features.get("Systolic BP", 120.0)) - 110.0) / 80.0),
            "direction": "Elevated systolic pressure raises cardiovascular concern.",
        },
        {
            "feature": "Sugar level",
            "impact": clamp((float(features.get("Sugar level", 100.0)) - 90.0) / 160.0),
            "direction": "Higher sugar level contributes to metabolic risk.",
        },
        {
            "feature": "Heart rate",
            "impact": clamp(abs(float(features.get("Heart rate", 75.0)) - 72.0) / 65.0),
            "direction": "Heart rate far from the resting range increases risk.",
        },
        {
            "feature": "Medical history",
            "impact": clamp(0.18 * sum(term in history for term in ("diabetes", "hypertension", "stroke", "heart", "kidney", "cancer"))),
            "direction": "Prior diagnoses and symptoms influence readmission and event risk.",
        },
    ]
    return sorted(contributions, key=lambda item: item["impact"], reverse=True)


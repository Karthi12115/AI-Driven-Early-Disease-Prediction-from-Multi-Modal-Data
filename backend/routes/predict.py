"""Prediction routes for the UI application."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.data_pipeline.preprocessing import preprocess_payload
from backend.models.multimodal_model import MultimodalRiskModel


router = APIRouter(prefix="/api", tags=["prediction"])
model = MultimodalRiskModel()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "multimodal-healthcare-api"}


@router.get("/sample")
def sample_payload() -> dict[str, Any]:
    return {
        "ehr": {
            "age": 62,
            "gender": "Male",
            "bloodPressure": "148/92",
            "sugarLevel": 166,
            "heartRate": 96,
            "medicalHistory": "Hypertension, diabetes, chest pain during exertion",
        },
        "genomics": {
            "source": "sample",
            "rows": [
                {"gene": "APOE4", "variant": "rs429358", "risk_score": 0.82},
                {"gene": "LDLR", "variant": "rs688", "risk_score": 0.67},
                {"gene": "MTHFR", "variant": "C677T", "risk_score": 0.58},
            ],
        },
        "wearable": {
            "simulated": True,
            "rows": [
                {"time": "00:00", "heart_rate": 82, "steps": 120, "spo2": 97, "sleep": 1.0},
                {"time": "04:00", "heart_rate": 88, "steps": 40, "spo2": 96, "sleep": 3.8},
                {"time": "08:00", "heart_rate": 101, "steps": 650, "spo2": 95, "sleep": 0.4},
                {"time": "12:00", "heart_rate": 108, "steps": 1800, "spo2": 95, "sleep": 0.0},
                {"time": "16:00", "heart_rate": 112, "steps": 2600, "spo2": 94, "sleep": 0.0},
                {"time": "20:00", "heart_rate": 96, "steps": 3300, "spo2": 96, "sleep": 0.0},
            ],
        },
        "medicalImage": {
            "hasImage": True,
            "name": "sample_chest_xray.png",
            "type": "image/png",
            "size": 512000,
            "findings": "Mild cardiomegaly with possible lower-zone opacity.",
        },
        "reportImage": {
            "hasImage": True,
            "name": "blood_report.png",
            "type": "image/png",
            "size": 214000,
            "reportText": "Elevated glucose and abnormal lipid profile.",
        },
    }


@router.post("/predict")
def predict(payload: dict[str, Any]) -> dict[str, Any]:
    processed = preprocess_payload(payload)
    return model.predict(processed)


"""Deterministic multimodal model mirroring a deep-learning fusion pipeline.

The production scaffold in ``src/models`` contains PyTorch modules. This file
keeps the UI demo lightweight by using deterministic math while preserving the
same architecture: EHR MLP encoder, genomics dense encoder, wearable GRU-style
temporal encoder, image CNN-style encoder, attention fusion, and prediction
layer. It is intended for live demonstrations before a trained checkpoint is
available.
"""

from __future__ import annotations

import math
from typing import Any

from backend.data_pipeline.preprocessing import clamp
from backend.explainability.feature_importance import ehr_feature_importance
from backend.explainability.modality_attention import dominant_modality, format_attention


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def softmax(scores: dict[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    max_score = max(scores.values())
    exps = {name: math.exp(score - max_score) for name, score in scores.items()}
    total = sum(exps.values()) or 1.0
    return {name: value / total for name, value in exps.items()}


class EHRMLPEncoder:
    name = "ehr"

    def encode(self, modality: dict[str, Any]) -> dict[str, Any]:
        vector = modality["vector"]
        age, systolic, diastolic, sugar, heart_rate, gender, history = vector
        risk = clamp(
            0.2
            + 0.18 * max(age, 0)
            + 0.18 * max(systolic, 0)
            + 0.08 * max(diastolic, 0)
            + 0.16 * max(sugar, 0)
            + 0.12 * abs(heart_rate)
            + 0.04 * gender
            + 0.24 * history
        )
        return {
            "risk": risk,
            "embedding": [risk, max(age, 0), max(systolic, 0), max(sugar, 0)],
            "confidence": 0.95 if modality.get("available") else 0.0,
        }


class GenomicsDenseEncoder:
    name = "genomics"

    def encode(self, modality: dict[str, Any]) -> dict[str, Any]:
        variant_density, marker_score, average_signal, elevated_share = modality["vector"]
        risk = clamp(0.14 + 0.18 * variant_density + 0.38 * marker_score + 0.18 * average_signal + 0.12 * elevated_share)
        return {
            "risk": risk,
            "embedding": [risk, marker_score, average_signal, elevated_share],
            "confidence": 0.85 if modality.get("available") else 0.0,
        }


class WearableGRUEncoder:
    name = "wearable"

    def encode(self, modality: dict[str, Any]) -> dict[str, Any]:
        heart_rate, variability, inactivity, low_spo2, low_sleep = modality["vector"]
        temporal_pressure = 0.45 * heart_rate + 0.18 * variability + 0.16 * inactivity + 0.15 * low_spo2 + 0.06 * low_sleep
        risk = clamp(0.16 + temporal_pressure)
        return {
            "risk": risk,
            "embedding": [risk, heart_rate, variability, low_spo2],
            "confidence": 0.88 if modality.get("available") else 0.0,
        }


class ImageCNNEncoder:
    name = "image"

    def encode(self, modality: dict[str, Any]) -> dict[str, Any]:
        scan_present, report_present, abnormal_terms, size_signal = modality["vector"]
        risk = clamp(0.18 + 0.08 * scan_present + 0.07 * report_present + 0.55 * abnormal_terms + 0.06 * size_signal)
        return {
            "risk": risk,
            "embedding": [risk, abnormal_terms, scan_present, report_present],
            "confidence": 0.78 if modality.get("available") else 0.0,
        }


class AttentionFusion:
    def fuse(self, encodings: dict[str, dict[str, Any]]) -> dict[str, Any]:
        available = {name: item for name, item in encodings.items() if item["confidence"] > 0}
        if not available:
            return {
                "fused_risk": 0.22,
                "weights": {name: 0.0 for name in encodings},
                "embedding": [0.22, 0.0, 0.0, 0.0],
            }

        scores = {
            name: 0.9 * item["risk"] + 0.35 * item["confidence"]
            for name, item in available.items()
        }
        weights = softmax(scores)
        full_weights = {name: weights.get(name, 0.0) for name in encodings}
        fused_risk = sum(available[name]["risk"] * weights[name] for name in available)

        embedding = [0.0, 0.0, 0.0, 0.0]
        for name, item in available.items():
            for index, value in enumerate(item["embedding"]):
                embedding[index] += weights[name] * value

        return {"fused_risk": clamp(fused_risk), "weights": full_weights, "embedding": embedding}


class PredictionLayer:
    def predict(self, fused: dict[str, Any], processed: dict[str, Any]) -> dict[str, float]:
        ehr_vector = processed["ehr"]["vector"]
        age = max(ehr_vector[0], 0.0)
        bp = max(ehr_vector[1], 0.0)
        sugar = max(ehr_vector[3], 0.0)
        heart_rate = abs(ehr_vector[4])
        history = ehr_vector[6]

        fused_risk = fused["fused_risk"]
        mortality = sigmoid(-2.0 + 3.2 * fused_risk + 0.42 * age + 0.24 * heart_rate + 0.25 * history)
        readmission = sigmoid(-1.8 + 3.0 * fused_risk + 0.33 * sugar + 0.22 * history)
        cardiac_neuro = sigmoid(-1.9 + 3.1 * fused_risk + 0.35 * bp + 0.22 * heart_rate + 0.18 * age)
        probability = clamp(0.38 * mortality + 0.29 * readmission + 0.33 * cardiac_neuro)

        return {
            "mortalityRisk": round(mortality, 3),
            "readmissionRisk": round(readmission, 3),
            "cardiacNeuroEventRisk": round(cardiac_neuro, 3),
            "overallProbability": round(probability, 3),
        }


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def predict_disease_category(processed: dict[str, Any]) -> dict[str, Any]:
    ehr_features = processed["ehr"]["features"]
    ehr_vector = processed["ehr"]["vector"]
    wearable_vector = processed["wearable"]["vector"]
    image_summary = processed["image"]["summary"]
    genomics_summary = processed["genomics"]["summary"]

    history = str(ehr_features.get("Medical history", "")).lower()
    image_terms = set(image_summary.get("risk_terms", []))
    markers = {str(marker).upper() for marker in genomics_summary.get("risk_markers", [])}

    age = max(ehr_vector[0], 0.0)
    bp = max(ehr_vector[1], 0.0)
    sugar = max(ehr_vector[3], 0.0)
    heart_rate = abs(ehr_vector[4])
    history_score = max(ehr_vector[6], 0.0)
    inactivity = max(wearable_vector[2], 0.0)
    low_spo2 = max(wearable_vector[3], 0.0)

    disease_scores = {
        "Cardiovascular disease": clamp(
            0.18
            + 0.24 * bp
            + 0.18 * heart_rate
            + 0.16 * age
            + 0.16 * history_score
            + (0.16 if _contains_any(history, ("hypertension", "cardiac", "heart", "chest pain")) else 0.0)
            + (0.12 if "LDLR" in markers else 0.0)
            + (0.12 if "cardiomegaly" in image_terms else 0.0)
        ),
        "Type 2 diabetes / metabolic disorder": clamp(
            0.16
            + 0.36 * sugar
            + 0.12 * inactivity
            + (0.22 if "diabetes" in history else 0.0)
            + (0.1 if "MTHFR" in markers else 0.0)
            + (0.08 if "elevated" in image_terms or "abnormal" in image_terms else 0.0)
        ),
        "Neurological event risk": clamp(
            0.14
            + 0.18 * age
            + 0.14 * heart_rate
            + (0.26 if "APOE4" in markers else 0.0)
            + (0.26 if _contains_any(history, ("stroke", "neuro", "seizure", "memory")) else 0.0)
            + (0.1 if "ischemia" in image_terms else 0.0)
        ),
        "Respiratory / pulmonary infection": clamp(
            0.12
            + 0.34 * low_spo2
            + (0.18 if _contains_any(history, ("asthma", "copd", "breath", "cough")) else 0.0)
            + (0.3 if image_terms.intersection({"opacity", "infiltrate", "infection", "edema"}) else 0.0)
        ),
        "Kidney / renal complication": clamp(
            0.1
            + 0.18 * bp
            + 0.18 * sugar
            + (0.34 if _contains_any(history, ("kidney", "renal", "creatinine")) else 0.0)
        ),
        "Cancer / abnormal lesion risk": clamp(
            0.08
            + (0.34 if image_terms.intersection({"lesion", "tumor", "nodule"}) else 0.0)
            + (0.18 if markers.intersection({"BRCA1", "BRCA2", "TP53", "EGFR", "JAK2"}) else 0.0)
            + (0.18 if _contains_any(history, ("cancer", "tumor", "weight loss")) else 0.0)
        ),
    }
    ranked = sorted(disease_scores.items(), key=lambda item: item[1], reverse=True)
    name, probability = ranked[0]
    evidence = []
    if bp > 0.2:
        evidence.append("elevated blood pressure")
    if sugar > 0.2:
        evidence.append("higher sugar level")
    if heart_rate > 0.2:
        evidence.append("heart-rate stress")
    if markers:
        evidence.append(f"genomic markers: {', '.join(sorted(markers)[:3])}")
    if image_terms:
        evidence.append(f"image/report terms: {', '.join(sorted(image_terms)[:3])}")
    if history_score > 0:
        evidence.append("medical history keywords")

    return {
        "name": name,
        "probability": round(probability, 3),
        "riskLevel": "Low" if probability < 0.4 else "Medium" if probability < 0.7 else "High",
        "supportingEvidence": evidence[:4] or ["available patient features"],
        "alternatives": [
            {"label": label, "value": round(score, 3)}
            for label, score in ranked[:5]
        ],
    }


class MultimodalRiskModel:
    def __init__(self) -> None:
        self.encoders = {
            "ehr": EHRMLPEncoder(),
            "genomics": GenomicsDenseEncoder(),
            "wearable": WearableGRUEncoder(),
            "image": ImageCNNEncoder(),
        }
        self.fusion = AttentionFusion()
        self.prediction_layer = PredictionLayer()

    def predict(self, processed: dict[str, Any]) -> dict[str, Any]:
        encodings = {
            name: encoder.encode(processed[name]) if processed[name]["available"] else {"risk": 0.0, "embedding": [0, 0, 0, 0], "confidence": 0.0}
            for name, encoder in self.encoders.items()
        }
        fused = self.fusion.fuse(encodings)
        outcomes = self.prediction_layer.predict(fused, processed)
        disease = predict_disease_category(processed)
        probability = outcomes["overallProbability"]
        risk_level = "Low" if probability < 0.4 else "Medium" if probability < 0.7 else "High"
        attention = fused["weights"]
        dominant = dominant_modality(attention)
        ehr_importance = ehr_feature_importance(processed["ehr"])

        return {
            "riskLevel": risk_level,
            "probability": probability,
            "predictedOutcome": {
                "mortalityRisk": outcomes["mortalityRisk"],
                "readmissionRisk": outcomes["readmissionRisk"],
                "cardiacNeuroEventRisk": outcomes["cardiacNeuroEventRisk"],
            },
            "predictedDisease": disease,
            "diseaseRisks": disease["alternatives"],
            "riskBreakdown": [
                {"label": "Mortality risk", "value": outcomes["mortalityRisk"]},
                {"label": "Readmission risk", "value": outcomes["readmissionRisk"]},
                {"label": "Cardiac / Neuro event risk", "value": outcomes["cardiacNeuroEventRisk"]},
            ],
            "modalityImportance": format_attention(attention),
            "dominantModality": dominant,
            "featureImportance": [
                {**item, "impact": round(float(item["impact"]), 3)}
                for item in ehr_importance
            ],
            "missingModalities": [name.title() if name != "ehr" else "EHR" for name in processed["missing_modalities"]],
            "modalityMask": processed["modality_mask"],
            "pipeline": [
                "Data input from UI",
                "EHR normalization and gender/history encoding",
                "Genomics feature vector creation",
                "Wearable time-series summarization",
                "CNN-style image/report signal extraction",
                "Attention-based multimodal fusion",
                "Risk classification and explainability",
            ],
            "wearableTrends": processed["wearable"]["rows"],
            "summaries": {
                "ehr": processed["ehr"]["features"],
                "genomics": processed["genomics"]["summary"],
                "wearable": processed["wearable"]["summary"],
                "image": processed["image"]["summary"],
            },
            "heatmap": {
                "enabled": bool(processed["image"]["available"]),
                "hotspots": [
                    {"x": 32, "y": 34, "strength": 0.58},
                    {"x": 58, "y": 52, "strength": 0.72},
                    {"x": 46, "y": 68, "strength": 0.45},
                ],
            },
        }

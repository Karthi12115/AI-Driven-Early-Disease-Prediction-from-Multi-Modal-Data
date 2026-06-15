"""Preprocess UI payloads into modality-specific feature summaries."""

from __future__ import annotations

import math
import re
from statistics import mean, pstdev
from typing import Any


EHR_FEATURES = ("age", "gender", "systolic_bp", "diastolic_bp", "sugar_level", "heart_rate", "medical_history")
GENOMIC_RISK_MARKERS = {
    "apoe4",
    "brca1",
    "brca2",
    "tp53",
    "ldlr",
    "mthfr",
    "hbb",
    "cftr",
    "egfr",
    "jak2",
}
REPORT_RISK_TERMS = {
    "opacity",
    "lesion",
    "cardiomegaly",
    "infiltrate",
    "ischemia",
    "stroke",
    "tumor",
    "nodule",
    "edema",
    "infection",
    "elevated",
    "abnormal",
}
HISTORY_RISK_TERMS = {
    "diabetes": 0.16,
    "hypertension": 0.15,
    "stroke": 0.2,
    "asthma": 0.08,
    "kidney": 0.14,
    "cardiac": 0.2,
    "heart": 0.19,
    "chest pain": 0.18,
    "smoking": 0.14,
    "cancer": 0.18,
}


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def safe_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    text = str(value).strip()
    if not text:
        return default
    try:
        return float(re.sub(r"[^0-9.\-]", "", text))
    except ValueError:
        return default


def has_content(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value)
    if isinstance(value, dict):
        return any(has_content(item) for item in value.values())
    return True


def parse_blood_pressure(value: Any) -> tuple[float, float]:
    if value is None:
        return 120.0, 80.0
    if isinstance(value, dict):
        return safe_float(value.get("systolic"), 120.0), safe_float(value.get("diastolic"), 80.0)
    numbers = re.findall(r"\d+(?:\.\d+)?", str(value))
    if len(numbers) >= 2:
        return safe_float(numbers[0], 120.0), safe_float(numbers[1], 80.0)
    systolic = safe_float(value, 120.0)
    return systolic, 80.0


def normalize_ehr(ehr: dict[str, Any] | None) -> dict[str, Any]:
    ehr = ehr or {}
    systolic, diastolic = parse_blood_pressure(ehr.get("bloodPressure") or ehr.get("blood_pressure"))
    gender = str(ehr.get("gender") or "unknown").strip().lower()
    history = str(ehr.get("medicalHistory") or ehr.get("medical_history") or "").strip().lower()
    age = safe_float(ehr.get("age"), 45.0)
    sugar = safe_float(ehr.get("sugarLevel") or ehr.get("sugar_level"), 100.0)
    heart_rate = safe_float(ehr.get("heartRate") or ehr.get("heart_rate"), 75.0)

    history_score = sum(weight for term, weight in HISTORY_RISK_TERMS.items() if term in history)
    encoded_gender = 1.0 if gender.startswith("m") else 0.6 if gender.startswith("f") else 0.5

    return {
        "available": has_content(ehr),
        "raw": ehr,
        "vector": [
            (age - 45.0) / 35.0,
            (systolic - 120.0) / 55.0,
            (diastolic - 80.0) / 35.0,
            (sugar - 100.0) / 105.0,
            (heart_rate - 75.0) / 55.0,
            encoded_gender,
            clamp(history_score),
        ],
        "features": {
            "Age": age,
            "Gender": gender.title() if gender else "Unknown",
            "Systolic BP": systolic,
            "Diastolic BP": diastolic,
            "Sugar level": sugar,
            "Heart rate": heart_rate,
            "Medical history": history,
        },
    }


def _row_values(row: Any) -> list[str]:
    if isinstance(row, dict):
        return [str(value).strip() for value in row.values()]
    if isinstance(row, (list, tuple)):
        return [str(value).strip() for value in row]
    return [str(row).strip()]


def _genomic_numeric_values(row: Any) -> list[float]:
    if isinstance(row, dict):
        values = []
        for key, raw_value in row.items():
            key_text = str(key).lower()
            if any(token in key_text for token in ("risk", "score", "prob", "signal", "value")):
                values.append(safe_float(raw_value, 0.0))
        return values
    if isinstance(row, (list, tuple)):
        return [safe_float(value, 0.0) for value in row if re.fullmatch(r"-?\d+(?:\.\d+)?", str(value).strip())]
    return []


def normalize_genomics(genomics: dict[str, Any] | list[Any] | None) -> dict[str, Any]:
    if isinstance(genomics, list):
        rows = genomics
        source = "uploaded"
    else:
        rows = (genomics or {}).get("rows") or []
        source = (genomics or {}).get("source") or "missing"

    numeric_values: list[float] = []
    marker_hits: set[str] = set()
    variant_count = 0

    for row in rows:
        joined = " ".join(_row_values(row)).lower()
        if joined:
            variant_count += 1
        for marker in GENOMIC_RISK_MARKERS:
            if marker in joined.replace(" ", "") or marker in joined:
                marker_hits.add(marker.upper())
        for value in _genomic_numeric_values(row):
            if math.isfinite(value):
                numeric_values.append(abs(value))

    average_signal = mean(numeric_values) if numeric_values else 0.0
    elevated_numeric_share = 0.0
    if numeric_values:
        elevated_numeric_share = sum(1 for value in numeric_values if value >= 0.65) / len(numeric_values)

    return {
        "available": bool(rows),
        "source": source,
        "rows": rows[:20],
        "vector": [
            clamp(variant_count / 30.0),
            clamp(len(marker_hits) / 5.0),
            clamp(average_signal if average_signal <= 1.0 else average_signal / 100.0),
            clamp(elevated_numeric_share),
        ],
        "summary": {
            "variant_count": variant_count,
            "risk_markers": sorted(marker_hits),
            "average_signal": round(average_signal, 3),
        },
    }


def normalize_wearable(wearable: dict[str, Any] | list[Any] | None) -> dict[str, Any]:
    if isinstance(wearable, list):
        rows = wearable
        simulated = False
    else:
        rows = (wearable or {}).get("rows") or []
        simulated = bool((wearable or {}).get("simulated"))

    heart_rates: list[float] = []
    steps: list[float] = []
    spo2_values: list[float] = []
    sleep_values: list[float] = []
    cleaned_rows: list[dict[str, float | str]] = []

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        heart_rate = safe_float(row.get("heart_rate") or row.get("heartRate") or row.get("hr"), 0.0)
        step_count = safe_float(row.get("steps") or row.get("step_count"), 0.0)
        spo2 = safe_float(row.get("spo2") or row.get("oxygen") or row.get("oxygen_saturation"), 98.0)
        sleep = safe_float(row.get("sleep") or row.get("sleep_hours"), 0.0)
        label = str(row.get("time") or row.get("timestamp") or index)

        if heart_rate > 0:
            heart_rates.append(heart_rate)
        if step_count >= 0:
            steps.append(step_count)
        if spo2 > 0:
            spo2_values.append(spo2)
        if sleep > 0:
            sleep_values.append(sleep)
        cleaned_rows.append(
            {
                "time": label,
                "heart_rate": round(heart_rate, 2),
                "steps": round(step_count, 2),
                "spo2": round(spo2, 2),
                "sleep": round(sleep, 2),
            }
        )

    avg_hr = mean(heart_rates) if heart_rates else 75.0
    hr_variability = pstdev(heart_rates) if len(heart_rates) > 1 else 0.0
    avg_steps = mean(steps) if steps else 3500.0
    avg_spo2 = mean(spo2_values) if spo2_values else 98.0
    avg_sleep = mean(sleep_values) if sleep_values else 7.0

    return {
        "available": bool(cleaned_rows),
        "simulated": simulated,
        "rows": cleaned_rows[-96:],
        "vector": [
            clamp((avg_hr - 70.0) / 60.0),
            clamp(hr_variability / 30.0),
            clamp((6000.0 - avg_steps) / 6000.0),
            clamp((96.0 - avg_spo2) / 10.0),
            clamp((6.0 - avg_sleep) / 6.0),
        ],
        "summary": {
            "average_heart_rate": round(avg_hr, 1),
            "heart_rate_variability": round(hr_variability, 1),
            "average_steps": round(avg_steps, 0),
            "average_spo2": round(avg_spo2, 1),
            "average_sleep": round(avg_sleep, 1),
        },
    }


def normalize_image(image_payload: dict[str, Any] | None, report_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    image_payload = image_payload or {}
    report_payload = report_payload or {}
    report_text = str(
        image_payload.get("findings")
        or image_payload.get("reportText")
        or report_payload.get("findings")
        or report_payload.get("reportText")
        or ""
    ).lower()
    joined_names = " ".join(
        str(value)
        for value in (
            image_payload.get("name"),
            image_payload.get("type"),
            report_payload.get("name"),
            report_payload.get("type"),
        )
        if value
    ).lower()
    combined = f"{report_text} {joined_names}"
    term_hits = sorted({term for term in REPORT_RISK_TERMS if term in combined})
    has_scan = bool(image_payload.get("hasImage") or image_payload.get("name") or image_payload.get("previewUrl"))
    has_report = bool(report_payload.get("hasImage") or report_payload.get("name") or report_text)

    size_signal = clamp((safe_float(image_payload.get("size"), 0.0) + safe_float(report_payload.get("size"), 0.0)) / 2_000_000.0)

    return {
        "available": has_scan or has_report,
        "vector": [
            1.0 if has_scan else 0.0,
            1.0 if has_report else 0.0,
            clamp(len(term_hits) / 5.0),
            size_signal,
        ],
        "summary": {
            "has_scan": has_scan,
            "has_report": has_report,
            "risk_terms": term_hits,
            "report_text": report_text,
        },
    }


def preprocess_payload(payload: dict[str, Any]) -> dict[str, Any]:
    ehr = normalize_ehr(payload.get("ehr"))
    genomics = normalize_genomics(payload.get("genomics"))
    wearable = normalize_wearable(payload.get("wearable"))
    image = normalize_image(payload.get("medicalImage"), payload.get("reportImage"))

    processed = {
        "ehr": ehr,
        "genomics": genomics,
        "wearable": wearable,
        "image": image,
    }
    processed["modality_mask"] = {name: data["available"] for name, data in processed.items()}
    processed["missing_modalities"] = [name for name, available in processed["modality_mask"].items() if not available]
    return processed

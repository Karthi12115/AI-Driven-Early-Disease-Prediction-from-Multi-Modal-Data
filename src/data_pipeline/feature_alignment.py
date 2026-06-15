"""Patient-level modality alignment and mask creation."""

from __future__ import annotations

from collections.abc import Mapping

from src.data_pipeline.preprocessing import DEFAULT_MODALITIES, modality_mask_from_record


def align_patient_modalities(
    modality_tables: Mapping[str, Mapping[str, object]],
    modalities: tuple[str, ...] = DEFAULT_MODALITIES,
) -> list[dict]:
    """Create patient records that share a common patient axis across modalities."""

    patient_ids: set[str] = set()
    for table in modality_tables.values():
        patient_ids.update(str(patient_id) for patient_id in table.keys())

    aligned: list[dict] = []
    for patient_id in sorted(patient_ids):
        record = {"patient_id": patient_id}
        for modality in modalities:
            record[modality] = modality_tables.get(modality, {}).get(patient_id)
        record["modality_mask"] = modality_mask_from_record(record, modalities)
        aligned.append(record)
    return aligned


def available_modalities(record: dict) -> list[str]:
    mask = record.get("modality_mask") or modality_mask_from_record(record)
    return [modality for modality, present in mask.items() if present]

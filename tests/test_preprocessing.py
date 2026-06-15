from src.data_pipeline.feature_alignment import align_patient_modalities
from src.data_pipeline.preprocessing import (
    impute_tabular,
    modality_mask_from_record,
    normalize_numeric,
    pad_or_truncate_sequence,
    tokenize_text,
)


def test_impute_and_normalize_tabular_records():
    records = [
        {"age": 60, "sex": "F"},
        {"age": None, "sex": ""},
        {"age": 80, "sex": "M"},
    ]

    imputed, fills = impute_tabular(records, numeric_fields=["age"], categorical_fields=["sex"])
    assert fills["age"] == 70.0
    assert imputed[1]["age"] == 70.0
    assert imputed[1]["sex"] == "unknown"

    normalized, stats = normalize_numeric(imputed, numeric_fields=["age"])
    assert "age" in stats
    assert len(normalized) == 3


def test_sequence_padding_and_truncation():
    sequence = [[1.0, 2.0], [3.0, 4.0]]
    assert pad_or_truncate_sequence(sequence, 1) == [[1.0, 2.0]]
    assert pad_or_truncate_sequence(sequence, 3) == [[1.0, 2.0], [3.0, 4.0], [0.0, 0.0]]


def test_text_tokenization_pads_to_max_length():
    ids, vocab = tokenize_text("High heart rate", max_length=5)
    assert len(ids) == 5
    assert vocab["high"] > 1
    assert ids[-1] == 0


def test_modality_alignment_builds_masks():
    aligned = align_patient_modalities(
        {
            "ehr": {"1": {"age": 70}},
            "image": {"2": "xray.png"},
        }
    )
    by_id = {record["patient_id"]: record for record in aligned}
    assert by_id["1"]["modality_mask"]["ehr"] is True
    assert by_id["1"]["modality_mask"]["image"] is False
    assert by_id["2"]["modality_mask"]["image"] is True


def test_modality_mask_marks_empty_values_missing():
    mask = modality_mask_from_record({"ehr": {}, "text": "", "image": "scan.png"}, ("ehr", "text", "image"))
    assert mask == {"ehr": True, "text": False, "image": True}

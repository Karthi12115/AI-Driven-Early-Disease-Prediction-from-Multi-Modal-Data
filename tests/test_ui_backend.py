from backend.data_pipeline.preprocessing import preprocess_payload
from backend.models.multimodal_model import MultimodalRiskModel
from backend.routes.predict import sample_payload


def test_ui_sample_payload_returns_prediction_and_explanations():
    processed = preprocess_payload(sample_payload())
    result = MultimodalRiskModel().predict(processed)

    assert result["riskLevel"] in {"Low", "Medium", "High"}
    assert 0 <= result["probability"] <= 1
    assert "mortalityRisk" in result["predictedOutcome"]
    assert result["predictedDisease"]["name"]
    assert 0 <= result["predictedDisease"]["probability"] <= 1
    assert result["diseaseRisks"]
    assert "EHR" in result["modalityImportance"]
    assert result["dominantModality"]["name"]
    assert result["featureImportance"]


def test_prediction_handles_missing_modalities():
    payload = {
        "ehr": {
            "age": 51,
            "gender": "Female",
            "bloodPressure": "126/82",
            "sugarLevel": 118,
            "heartRate": 78,
            "medicalHistory": "",
        }
    }

    result = MultimodalRiskModel().predict(preprocess_payload(payload))

    assert result["riskLevel"] in {"Low", "Medium", "High"}
    assert result["predictedDisease"]["name"]
    assert result["modalityMask"]["ehr"] is True
    assert result["modalityMask"]["genomics"] is False
    assert result["modalityMask"]["wearable"] is False
    assert result["modalityMask"]["image"] is False
    assert set(result["missingModalities"]) == {"Genomics", "Wearable", "Image"}

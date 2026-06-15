import pytest

torch = pytest.importorskip("torch")

from src.models.fusion_attention import AttentionFusion


def test_attention_fusion_ignores_missing_modality():
    fusion = AttentionFusion(embedding_dim=8, modalities=["ehr", "image"])
    features = {
        "ehr": torch.ones(2, 8),
        "image": torch.zeros(2, 8),
    }
    mask = {
        "ehr": torch.tensor([True, True]),
        "image": torch.tensor([False, True]),
    }

    fused, attention = fusion(features, mask)
    assert fused.shape == (2, 8)
    assert attention["image"][0].item() == pytest.approx(0.0)
    assert attention["ehr"][0].item() == pytest.approx(1.0)


def test_attention_fusion_handles_all_missing_row():
    fusion = AttentionFusion(embedding_dim=8, modalities=["ehr", "image"])
    features = {
        "ehr": torch.ones(1, 8),
        "image": torch.zeros(1, 8),
    }
    mask = {
        "ehr": torch.tensor([False]),
        "image": torch.tensor([False]),
    }

    fused, attention = fusion(features, mask)
    assert fused.shape == (1, 8)
    assert attention["ehr"][0].item() == pytest.approx(1.0)

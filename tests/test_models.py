import pytest

torch = pytest.importorskip("torch")

from src.train import build_model, create_demo_batch
from src.utils.io_utils import load_config


def test_multimodal_model_forward_shapes():
    config = load_config()
    model = build_model(config)
    batch, _ = create_demo_batch(config, batch_size=2)

    output = model(batch)

    assert output["logits"].shape == (2, len(config["model"]["outcomes"]))
    assert output["probabilities"].shape == output["logits"].shape
    assert set(output["attention"].keys()) == {"ehr", "genomics", "wearable", "image", "text"}

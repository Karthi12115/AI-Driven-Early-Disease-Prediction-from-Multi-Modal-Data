import pytest

torch = pytest.importorskip("torch")

from src.infer import load_model, predict_batch
from src.train import create_demo_batch, train_demo
from src.utils.io_utils import load_config


def test_demo_training_checkpoint_supports_prediction(tmp_path):
    checkpoint = tmp_path / "demo_model.pt"
    train_demo(output_path=checkpoint)

    config = load_config()
    model = load_model(checkpoint, config)
    batch, _ = create_demo_batch(config, batch_size=1)
    result = predict_batch(model, batch)

    assert result["outcomes"] == config["model"]["outcomes"]
    assert len(result["probabilities"]) == 1
    assert "ehr" in result["attention"]

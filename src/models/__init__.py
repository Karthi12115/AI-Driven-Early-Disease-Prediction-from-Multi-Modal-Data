"""Model components for multimodal risk prediction."""

try:
    from src.models.multimodal_model import MultimodalRiskModel

    __all__ = ["MultimodalRiskModel"]
except ImportError:
    __all__ = []

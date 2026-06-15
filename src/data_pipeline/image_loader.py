"""Load medical image paths and arrays."""

from __future__ import annotations

from pathlib import Path


IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff")


def list_image_paths(directory: str | Path) -> list[Path]:
    root = Path(directory)
    return sorted(path for path in root.rglob("*") if path.suffix.lower() in IMAGE_EXTENSIONS)


def load_image_array(path: str | Path):
    from PIL import Image
    import numpy as np

    with Image.open(path) as image:
        return np.asarray(image.convert("RGB"))

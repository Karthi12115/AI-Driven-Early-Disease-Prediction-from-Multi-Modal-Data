"""Load and prepare clinical text notes."""

from __future__ import annotations

from pathlib import Path


def load_text_file(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_text_directory(directory: str | Path) -> dict[str, str]:
    root = Path(directory)
    return {path.stem: load_text_file(path) for path in sorted(root.glob("*.txt"))}

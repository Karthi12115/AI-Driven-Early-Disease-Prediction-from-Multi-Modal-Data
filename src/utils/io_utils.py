"""Input/output helpers used across the project."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_path(path: str | Path, base: str | Path | None = None) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return (Path(base) if base is not None else project_root()) / candidate


def ensure_dir(path: str | Path) -> Path:
    resolved = resolve_path(path)
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def load_yaml(path: str | Path) -> dict[str, Any]:
    resolved = resolve_path(path)
    with resolved.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def load_config(
    config_path: str | Path = "config/config.yaml",
    paths_path: str | Path = "config/paths.yaml",
) -> dict[str, Any]:
    config = load_yaml(config_path)
    config["paths"] = load_yaml(paths_path)
    return config


def save_json(data: Any, path: str | Path) -> Path:
    resolved = resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
    return resolved


def load_json(path: str | Path) -> Any:
    resolved = resolve_path(path)
    with resolved.open("r", encoding="utf-8") as file:
        return json.load(file)

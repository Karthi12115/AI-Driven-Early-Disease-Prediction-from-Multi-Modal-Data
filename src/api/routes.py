"""FastAPI routes for a lightweight demo backend."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/predict/demo")
def predict_demo() -> dict:
    from src.infer import infer_demo

    return infer_demo()

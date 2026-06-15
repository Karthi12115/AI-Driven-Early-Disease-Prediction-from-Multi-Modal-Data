"""FastAPI entry point for the UI-based multimodal prediction app."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.routes.predict import router as predict_router
from backend.routes.upload import router as upload_router

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = PROJECT_ROOT / "frontend"


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI-Driven Early Disease Prediction API",
        description="Multimodal risk prediction API for EHR, genomics, wearable, and medical image/report inputs.",
        version="1.0.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(predict_router)
    app.include_router(upload_router)

    if FRONTEND_ROOT.exists():
        app.mount("/src", StaticFiles(directory=FRONTEND_ROOT / "src"), name="frontend-src")
        app.mount("/public", StaticFiles(directory=FRONTEND_ROOT / "public"), name="frontend-public")

        @app.get("/", include_in_schema=False)
        def frontend_index() -> FileResponse:
            return FileResponse(FRONTEND_ROOT / "index.html")

    return app


app = create_app()

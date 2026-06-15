"""Upload helper route.

The UI reads files locally for preview and sends compact metadata to
``/api/predict``. This route exists to document the upload boundary and can be
extended later for persisted files.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter


router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload/metadata")
def accept_upload_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    return {"status": "accepted", "received": payload}


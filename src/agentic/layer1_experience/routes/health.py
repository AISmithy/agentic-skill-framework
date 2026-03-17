"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness():
    return {"status": "ready"}

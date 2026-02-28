"""
Engine 1 — CrowdSignal Router

Endpoints for the NLP chat pipeline.
Owner: Bhoomi
"""

from fastapi import APIRouter
from app.models.schemas import CrowdSignal

router = APIRouter()


@router.get("/latest")
async def get_latest_signals(line: str = None, limit: int = 10):
    """Get latest crowd signals from NLP pipeline."""
    # TODO: Query Neo4j for recent :CrowdSignal nodes
    return {"signals": [], "message": "wire to neo4j"}


@router.get("/score/{train_id}")
async def get_crowd_score(train_id: str):
    """Get computed crowd score for a specific train."""
    # TODO: Base score + multipliers + live override
    return {"train_id": train_id, "score": 0, "message": "wire to crowd engine"}


@router.post("/ingest")
async def ingest_signal(signal: CrowdSignal):
    """Manually push a crowd signal (for testing / demo)."""
    # TODO: Write to Neo4j as :CrowdSignal node
    return {"status": "ok", "signal": signal.model_dump()}

"""
Engine 3 — DisruptionBrain Router

Cascade prediction and rerouting.
Owner: Bhoomi
"""

from fastapi import APIRouter
from app.models.schemas import DisruptionEvent, RerouteCard

router = APIRouter()


@router.post("/trigger")
async def trigger_disruption(event: DisruptionEvent):
    """Simulate a train cancellation → cascade → reroute cards."""
    # TODO: Cascade engine → identify affected trains → reroute
    return {"disruption": event.model_dump(), "cascade": [], "reroutes": []}


@router.get("/cascade/{train_id}")
async def get_cascade(train_id: str):
    """Get cascade risk for downstream trains if this train cancels."""
    # TODO: Fetch next 3 trains on same line, calculate surge
    return {"train_id": train_id, "cascade_risks": []}


@router.get("/reroute/{user_id}")
async def get_reroute(user_id: str):
    """Get personalized reroute card for a user affected by disruption."""
    # TODO: User profile + alternate trains + multimodal options
    return {"user_id": user_id, "reroute": None}

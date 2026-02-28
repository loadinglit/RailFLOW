"""
Engine 2 — PersonalGuard Router

Proactive alerts for commuters.
Owner: Bhoomi
"""

from fastapi import APIRouter
from app.models.schemas import AlertMessage

router = APIRouter()


@router.get("/user/{user_id}/routine")
async def get_user_routine(user_id: str):
    """Get a user's learned commute routine from Knowledge Graph."""
    # TODO: Cypher query for user profile
    return {"user_id": user_id, "routine": None, "message": "wire to neo4j"}


@router.get("/user/{user_id}/alert")
async def get_alert(user_id: str):
    """Generate today's proactive alert for this user."""
    # TODO: Crowd score + multipliers + best option → AlertMessage
    return {"user_id": user_id, "alert": None, "message": "wire to alert engine"}


@router.post("/trigger-all")
async def trigger_all_alerts():
    """Manually fire alerts for all demo users (for demo)."""
    # TODO: Loop through demo users, generate and push alerts
    return {"triggered": 0, "message": "wire to FCM"}

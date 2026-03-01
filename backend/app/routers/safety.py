"""
Safety Intelligence Router — Passenger Alerts + Police Analytics.
"""

from fastapi import APIRouter, Query
from app.engines.safety_engine import get_recent_alerts, get_analytics

router = APIRouter()


@router.get("/alerts")
async def safety_alerts(language: str = Query("en", description="Language: en, hi, mr")):
    """Get recent complaint-driven safety alerts for passengers."""
    return get_recent_alerts(language)


@router.get("/analytics")
async def safety_analytics():
    """Get complaint analytics + AI patrol recommendation for police dashboard."""
    return get_analytics()
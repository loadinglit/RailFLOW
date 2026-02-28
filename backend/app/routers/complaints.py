"""
Police Dashboard API — Complaint Management Endpoints.

GET  /api/complaints/          → list all complaints (with filters)
GET  /api/complaints/{ref}     → get single complaint details
PATCH /api/complaints/{ref}/status → update status (acknowledge/resolve/reject)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.engines.jansuraksha.neo4j_context import (
    list_complaints,
    get_complaint,
    update_complaint_status,
)
from app.services.notifications import notify_user
from app.utils.logger import get_logger

log = get_logger("router.complaints")

router = APIRouter()


class StatusUpdate(BaseModel):
    """Body for PATCH status updates from police dashboard."""
    status: str  # "acknowledged" | "resolved" | "rejected"
    note: str = ""


@router.get("/")
async def get_complaints(
    status: Optional[str] = None,
    type: Optional[str] = None,
):
    """
    List all complaints with optional filters.

    Query params:
    - status: filed | acknowledged | resolved | rejected
    - type: theft | robbery | assault | etc.
    """
    log.info("GET /complaints — status=%s, type=%s", status, type)
    try:
        complaints = list_complaints(status_filter=status, type_filter=type)
        return {"complaints": complaints, "count": len(complaints)}
    except Exception as e:
        log.error("GET /complaints FAILED: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ref}")
async def get_complaint_detail(ref: str):
    """Get a single complaint by reference number."""
    log.info("GET /complaints/%s", ref)
    try:
        complaint = get_complaint(ref)
        if not complaint or not complaint.get("ref"):
            raise HTTPException(status_code=404, detail=f"Complaint {ref} not found")
        return {"complaint": complaint}
    except HTTPException:
        raise
    except Exception as e:
        log.error("GET /complaints/%s FAILED: %s", ref, e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{ref}/status")
async def update_status(ref: str, update: StatusUpdate):
    """
    Update complaint status from police dashboard.

    Valid statuses: acknowledged, resolved, rejected
    Note is required for rejection.
    """
    log.info("PATCH /complaints/%s/status → %s", ref, update.status)

    valid_statuses = {"acknowledged", "resolved", "rejected"}
    if update.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    if update.status == "rejected" and not update.note.strip():
        raise HTTPException(status_code=400, detail="A reason is required when rejecting a complaint")

    try:
        result = update_complaint_status(ref, update.status, update.note)
        if not result or not result.get("ref"):
            raise HTTPException(status_code=404, detail=f"Complaint {ref} not found")

        # Send notification to user
        user_id = result.get("user_id")
        if user_id:
            await notify_user(user_id, ref, update.status, update.note)

        return {
            "success": True,
            "ref": ref,
            "new_status": update.status,
            "user_notified": bool(user_id),
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error("PATCH /complaints/%s/status FAILED: %s", ref, e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
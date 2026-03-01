"""
Jan Suraksha Bot — User & Complaint Data Layer.

All data lives in SQLite. Zero cloud dependency.
File kept as neo4j_context.py to avoid changing imports everywhere.
"""

from app.db import get_db
from app.utils.logger import get_logger

log = get_logger("jansuraksha.data")


def load_user_context(user_id: str) -> dict:
    """Load user profile + complaint count from SQLite."""
    log.info("Loading user context for user_id=%s", user_id)

    db = get_db()
    try:
        user = db.execute("""
            SELECT u.*, COUNT(c.id) AS previous_complaints
            FROM users u
            LEFT JOIN complaints c ON c.user_id = u.id
            WHERE u.id = ?
            GROUP BY u.id
        """, (user_id,)).fetchone()

        if not user:
            log.warning("User %s NOT FOUND", user_id)
            return {"user_id": user_id, "found": False}

        ctx = {
            "user_id": user_id,
            "found": True,
            "name": user["name"],
            "email": user["email"],
            "language_pref": user["language_pref"],
            "phone": user["phone"],
            "address": user["address"],
            "previous_complaints": user["previous_complaints"],
        }
        log.info("User found: name=%s, phone=%s", ctx["name"], ctx.get("phone"))
        return ctx
    finally:
        db.close()


def save_complaint(user_id: str, complaint_data: dict) -> dict:
    """Save a complaint to SQLite. Returns ref + status."""
    ref = complaint_data["ref"]
    log.info("Saving complaint for user_id=%s, ref=%s", user_id, ref)

    db = get_db()
    try:
        db.execute("""
            INSERT INTO complaints (ref, user_id, incident_type, severity, status,
                complaint_text, user_message, authority, date_filed,
                from_station, to_station)
            VALUES (?, ?, ?, ?, 'filed', ?, ?, ?, ?, ?, ?)
        """, (
            ref,
            user_id,
            complaint_data.get("incident_type", "general"),
            complaint_data.get("severity", "medium"),
            complaint_data.get("complaint_text", ""),
            complaint_data.get("user_message", ""),
            complaint_data.get("authority", ""),
            complaint_data.get("date_filed", ""),
            complaint_data.get("from_station", ""),
            complaint_data.get("to_station", ""),
        ))
        db.commit()
        log.info("Complaint saved: ref=%s", ref)
        return {"ref": ref, "status": "filed"}
    except Exception as e:
        log.error("Failed to save complaint: %s", e)
        return {}
    finally:
        db.close()


def update_complaint_status(ref: str, status: str, officer_note: str = "") -> dict:
    """Update complaint status. Returns complaint + user info for notification."""
    from datetime import datetime
    now = datetime.now().isoformat()

    log.info("Updating complaint ref=%s -> status=%s", ref, status)

    db = get_db()
    try:
        db.execute("""
            UPDATE complaints SET status = ?, officer_note = ?, updated_at = ?
            WHERE ref = ?
        """, (status, officer_note, now, ref))
        db.commit()

        row = db.execute("""
            SELECT c.*, u.name AS user_name, u.email AS user_email
            FROM complaints c
            JOIN users u ON u.id = c.user_id
            WHERE c.ref = ?
        """, (ref,)).fetchone()

        if row:
            result = dict(row)
            log.info("Complaint updated: ref=%s, status=%s, user=%s",
                     ref, status, result.get("user_name"))
            return result

        log.warning("Complaint ref=%s not found", ref)
        return {}
    finally:
        db.close()


def list_complaints(status_filter: str = None, type_filter: str = None) -> list:
    """List complaints with optional filters."""
    db = get_db()
    try:
        query = """
            SELECT c.ref, c.incident_type, c.status, c.severity,
                   c.complaint_text, c.user_message, c.authority,
                   c.date_filed, c.officer_note, c.updated_at,
                   u.name AS user_name, u.id AS user_id,
                   u.language_pref AS user_language
            FROM complaints c
            JOIN users u ON u.id = c.user_id
        """
        conditions = []
        params = []

        if status_filter:
            conditions.append("c.status = ?")
            params.append(status_filter)
        if type_filter:
            conditions.append("c.incident_type = ?")
            params.append(type_filter)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY c.date_filed DESC"

        rows = db.execute(query, params).fetchall()
        result = [dict(r) for r in rows]
        log.info("Listed %d complaints (status=%s, type=%s)",
                 len(result), status_filter, type_filter)
        return result
    finally:
        db.close()


def get_complaint(ref: str) -> dict:
    """Get single complaint by ref."""
    db = get_db()
    try:
        row = db.execute("""
            SELECT c.*, u.name AS user_name, u.id AS user_id
            FROM complaints c
            JOIN users u ON u.id = c.user_id
            WHERE c.ref = ?
        """, (ref,)).fetchone()
        return dict(row) if row else {}
    finally:
        db.close()
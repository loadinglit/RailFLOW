"""
Notification Service — Email + SMS on complaint status changes.

Sends email via SMTP (Gmail) and SMS via Twilio when configured.
Falls back to logging when credentials aren't set (demo mode).
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.db import get_db
from app.utils.logger import get_logger

log = get_logger("notifications")

# ── Config (from env) ─────────────────────────────────────────

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

TWILIO_SID = os.getenv("TWILIO_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN", "")
TWILIO_FROM = os.getenv("TWILIO_FROM", "")


# ── Helpers ───────────────────────────────────────────────────

def _get_user_contact(user_id: str) -> dict:
    """Pull user's email from SQLite."""
    db = get_db()
    try:
        row = db.execute(
            "SELECT name, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else {}
    finally:
        db.close()


def _build_message(ref: str, status: str, note: str) -> tuple[str, str]:
    """Build subject and body for the notification."""
    if status == "acknowledged":
        subject = f"Complaint {ref} — Received & Under Investigation"
        body = (
            f"Your complaint {ref} has been received by the railway police. "
            f"An officer is now working on your case."
        )
    elif status == "resolved":
        subject = f"Complaint {ref} — Resolved"
        body = f"Your complaint {ref} has been resolved."
        if note:
            body += f" Officer's note: {note}"
    elif status == "rejected":
        subject = f"Complaint {ref} — Update"
        body = f"Your complaint {ref} has been reviewed."
        if note:
            body += f" Reason: {note}"
    else:
        subject = f"Complaint {ref} — Status Update"
        body = f"Your complaint {ref} status has been updated to: {status}."
        if note:
            body += f" Note: {note}"
    return subject, body


# ── Email ─────────────────────────────────────────────────────

def _send_email(to_email: str, subject: str, body: str):
    """Send email via SMTP. Silently fails if not configured."""
    if not SMTP_USER or not to_email:
        log.info("[email] Skipped — SMTP not configured or no recipient email")
        return

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        log.info("[email] Sent to %s — %s", to_email, subject)
    except Exception as e:
        log.error("[email] Failed to send to %s: %s", to_email, e)


# ── SMS ───────────────────────────────────────────────────────

def _send_sms(to_phone: str, body: str):
    """Send SMS via Twilio. Silently fails if not configured."""
    if not TWILIO_SID or not to_phone:
        log.info("[sms] Skipped — Twilio not configured or no phone number")
        return

    try:
        from twilio.rest import Client
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(body=body, from_=TWILIO_FROM, to=to_phone)
        log.info("[sms] Sent to %s", to_phone)
    except Exception as e:
        log.error("[sms] Failed to send to %s: %s", to_phone, e)


# ── Public API ────────────────────────────────────────────────

async def notify_user(user_id: str, ref: str, status: str, note: str = ""):
    """
    Send email + SMS notification to user about complaint status change.

    Works in demo mode (just logs) when SMTP/Twilio aren't configured.
    """
    user = _get_user_contact(user_id)
    subject, body = _build_message(ref, status, note)

    log.info("[notify] ref=%s, status=%s, user=%s (%s)",
             ref, status, user.get("name", "unknown"), user_id)

    _send_email(user.get("email"), subject, body)
    _send_sms(user.get("phone"), body)

    # Always log for demo visibility
    log.info("[notify] DONE — %s → user=%s, status=%s", ref, user_id, status)
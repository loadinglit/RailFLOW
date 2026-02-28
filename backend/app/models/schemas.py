"""
RailMind Shared Data Models.

These are the contracts between engines. When CrowdSignal writes data,
PersonalGuard and DisruptionBrain read the same shape.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


# ── Enums ──────────────────────────────────────────────────────

class SignalType(str, Enum):
    CROWD = "crowd"
    DELAY = "delay"
    CANCEL = "cancel"
    FIGHT = "fight"
    PLATFORM_CHANGE = "platform_change"
    SIGNAL_FAIL = "signal_fail"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    DANGER = "danger"


class LineName(str, Enum):
    WESTERN = "WR"
    CENTRAL = "CR"
    HARBOUR = "HR"


# ── Engine 1: CrowdSignal ─────────────────────────────────────

class CrowdSignal(BaseModel):
    """Output of NLP pipeline — one structured signal from chat."""
    train_number: Optional[str] = None
    station: Optional[str] = None
    line: Optional[LineName] = None
    signal_type: SignalType
    severity: Severity
    raw_text: str
    timestamp: datetime
    source: str = "mindicator_chat"


# ── Engine 2: PersonalGuard ────────────────────────────────────

class UserProfile(BaseModel):
    """A commuter's learned routine."""
    user_id: str
    name: str
    origin: str
    destination: str
    line: LineName
    usual_train: str
    usual_departure: str  # "08:05"
    flexibility_score: float  # 0.0 (rigid) to 1.0 (flexible)


class AlertMessage(BaseModel):
    """Push notification content sent to user's phone."""
    user_id: str
    title: str
    body: str
    best_option: Optional[str] = None
    alternative: Optional[str] = None
    crowd_score: int  # 0-100
    reasons: list[str]


# ── Engine 3: DisruptionBrain ──────────────────────────────────

class DisruptionEvent(BaseModel):
    """A detected disruption — cancellation, signal failure, etc."""
    train_number: str
    line: LineName
    disruption_type: str  # cancel / delay / megablock / signal_fail
    station: Optional[str] = None
    detected_at: datetime


class CascadeRisk(BaseModel):
    """Predicted overflow on downstream trains after a disruption."""
    source_train: str
    affected_train: str
    predicted_surge_percent: float  # e.g. 140 means 140% capacity
    confidence: float  # 0-1


class RerouteCard(BaseModel):
    """Full reroute recommendation pushed to affected users."""
    user_id: str
    disrupted_train: str
    options: list[dict]  # [{train, platform, crowd_score, time_diff, notes}]
    multimodal_option: Optional[str] = None  # bus/metro fallback


# ── Engine 4: Jan Suraksha Bot ─────────────────────────────────

class ChatRequest(BaseModel):
    """Incoming message to Jan Suraksha Bot."""
    user_id: str
    message: str
    language: str = "en"  # en / hi / mr


class ChatResponse(BaseModel):
    """Bot response with all generated artifacts."""
    response: str
    complaint_draft: Optional[str] = None
    authority: Optional[str] = None
    compensation: Optional[str] = None
    cpgrams_ref: Optional[str] = None
    follow_up_date: Optional[str] = None

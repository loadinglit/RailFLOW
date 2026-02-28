"""
RailSense Data Models.

Engine A: FootGuard — platform safety detection
Engine B: TrespassMap — station risk prediction
Engine C: Jan Suraksha Bot — complaint filing (Dhruv)
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


# ── Enums ──────────────────────────────────────────────────────

class DangerLevel(str, Enum):
    SAFE = "safe"
    CAUTION = "caution"
    DANGER = "danger"
    CRITICAL = "critical"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LineName(str, Enum):
    WESTERN = "WR"
    CENTRAL = "CR"
    HARBOUR = "HR"


# ── Engine A: FootGuard ───────────────────────────────────────

class AnalyzeRequest(BaseModel):
    """Image upload for FootGuard analysis."""
    image_base64: str
    station: Optional[str] = None
    camera_id: Optional[str] = None


class DetectionResult(BaseModel):
    """What FootGuard detected in a single frame."""
    footboard_detected: bool = False
    persons_at_risk: int = 0
    door_overcrowding: bool = False
    platform_rush: bool = False
    danger_level: DangerLevel = DangerLevel.SAFE
    confidence: float = 0.0
    description: str = ""


class DetectionEvent(BaseModel):
    """Full FootGuard analysis output — stored in Neo4j."""
    detection: DetectionResult
    station: Optional[str] = None
    station_historical_risk: Optional[float] = None
    recommended_action: str = ""
    reasoning: str = ""
    timestamp: datetime = None
    source: str = "footguard"


# ── Engine B: TrespassMap ─────────────────────────────────────

class StationRisk(BaseModel):
    """Risk score for a single station."""
    station: str
    line: LineName
    risk_score: int  # 0-100
    risk_level: RiskLevel
    annual_deaths: int = 0
    trespass_deaths: int = 0
    footboard_deaths: int = 0
    has_fob: bool = True  # foot overbridge
    platform_count: int = 2
    risk_factors: list[str] = []
    rpf_recommendation: str = ""
    lat: Optional[float] = None
    lng: Optional[float] = None


class RiskMapResponse(BaseModel):
    """Full risk map — all stations."""
    stations: list[StationRisk]
    high_risk_count: int
    timestamp: datetime
    weather_factor: Optional[str] = None


# ── Engine C: Jan Suraksha Bot (Dhruv) ────────────────────────

class ChatRequest(BaseModel):
    """Incoming message to Jan Suraksha Bot."""
    user_id: str
    message: str
    language: str = "en"  # en / hi / mr
    context: Optional[dict] = None  # auto-filled by FootGuard trigger


class ActionOption(BaseModel):
    """A suggested action the user can take (shown as button in UI)."""
    id: str
    label: str
    description: str


class ChatResponse(BaseModel):
    """Bot response with all generated artifacts."""
    response: str
    options: Optional[list[ActionOption]] = None
    complaint_draft: Optional[str] = None
    authority: Optional[str] = None
    compensation: Optional[str] = None
    cpgrams_ref: Optional[str] = None
    follow_up_date: Optional[str] = None

"""
RailFlow — FastAPI Application

Intelligent Train Routing for Mumbai Suburban Railways.
- Train Search with Crowd Badges (crowd intelligence engine)
- Jan Suraksha Bot (Dhruv) — Legal aid chatbot
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import shutdown
from app.routers import trains, bot


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[railflow] Starting up...")
    yield
    shutdown()
    print("[railflow] Shut down.")


app = FastAPI(
    title="RailFlow API",
    description="Intelligent Train Routing for Mumbai Suburban Railways — mIndicator AI Hackathon 2026",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount routers ─────────────────────────────────────────────
app.include_router(trains.router, prefix="/api/trains", tags=["Train Search"])
app.include_router(bot.router, prefix="/api/bot", tags=["Jan Suraksha Bot"])


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "project": "RailFlow",
        "version": "2.0.0",
        "features": {
            "trains": "Smart train search with crowd badges (GREEN/YELLOW/RED)",
            "bot": "Jan Suraksha Bot — Legal aid for railway passengers",
        },
    }

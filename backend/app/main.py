"""
RailMind — FastAPI Application

All 4 engines exposed as REST endpoints.
Bhoomi's engines: CrowdSignal, PersonalGuard, DisruptionBrain
Dhruv's engine: Jan Suraksha Bot (RAG on Milvus + Neo4j context)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import shutdown
from app.routers import crowdsignal, personalguard, disruption, bot


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — connections are lazy, created on first use
    print("[railmind] Starting up...")
    yield
    # Shutdown
    shutdown()
    print("[railmind] Shut down.")


app = FastAPI(
    title="RailMind API",
    description="AI Intelligence Layer for Mumbai Suburban Railways",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hackathon — open CORS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount engine routers ───────────────────────────────────────
app.include_router(crowdsignal.router, prefix="/api/crowdsignal", tags=["Engine 1 - CrowdSignal"])
app.include_router(personalguard.router, prefix="/api/guard", tags=["Engine 2 - PersonalGuard"])
app.include_router(disruption.router, prefix="/api/disruption", tags=["Engine 3 - DisruptionBrain"])
app.include_router(bot.router, prefix="/api/bot", tags=["Engine 4 - Jan Suraksha Bot"])


@app.get("/health")
async def health():
    return {"status": "ok", "project": "RailMind", "engines": 4}

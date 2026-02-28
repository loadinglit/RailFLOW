"""
RailFLOW — FastAPI Application

Jan Suraksha Bot + Police Dashboard.
Auth via SQLite. Legal RAG via Zilliz.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.routers import bot, complaints, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — init SQLite tables
    init_db()
    print("[railflow] Starting up...")
    yield
    print("[railflow] Shut down.")


app = FastAPI(
    title="RailFLOW API",
    description="Jan Suraksha Bot — Railway Passenger Safety Platform",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(bot.router, prefix="/api/bot", tags=["Jan Suraksha Bot"])
app.include_router(complaints.router, prefix="/api/complaints", tags=["Police Dashboard"])


@app.get("/health")
async def health():
    return {"status": "ok", "project": "RailFLOW"}
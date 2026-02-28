"""
RailFLOW Core — Shared connections.

OpenAI (via LiteLLM proxy) for LLM calls.
Milvus/Zilliz for legal RAG vector search.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

# Load .env from project root
_env_path = Path(__file__).resolve().parents[2] / ".env"
if not _env_path.exists():
    _env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_env_path)


# ── Milvus / Zilliz Connection (Vector Store for RAG) ──────────

_milvus_client = None


def get_milvus_client():
    """Get or create a MilvusClient connected to Zilliz Cloud."""
    global _milvus_client
    if _milvus_client is None:
        from pymilvus import MilvusClient
        uri = os.getenv("ZILLIZ_URI")
        token = os.getenv("ZILLIZ_TOKEN")
        if uri and token:
            _milvus_client = MilvusClient(uri=uri, token=token)
        else:
            _milvus_client = MilvusClient(uri="http://localhost:19530")
        print("[core] Milvus/Zilliz connected")
    return _milvus_client


# ── Model Names ───────────────────────────────────────────────

MODEL_SMART = os.getenv("MODEL_SMART", "azure-gpt-4o-mini")
MODEL_FAST = os.getenv("MODEL_FAST", "azure-gpt-4o-mini")
MODEL_EMBED = os.getenv("MODEL_EMBED", "text-embedding-3-small")


# ── OpenAI Client ──────────────────────────────────────────────

_openai_client = None


def get_openai_client() -> OpenAI:
    """Get or create an OpenAI client."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL") or None,
        )
    return _openai_client


def embed_text(text: str) -> list[float]:
    """Embed text using embedding model."""
    client = get_openai_client()
    response = client.embeddings.create(model=MODEL_EMBED, input=text)
    return response.data[0].embedding


# ── Cleanup ────────────────────────────────────────────────────

def shutdown():
    global _milvus_client
    if _milvus_client:
        _milvus_client.close()
        _milvus_client = None
    print("[core] Connections closed")
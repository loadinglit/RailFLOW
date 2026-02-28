"""
RailFLOW Core — Shared connections.

OpenAI (via LiteLLM proxy) for LLM calls.
Milvus/Zilliz for legal RAG vector search.
Neo4j for train data + crowd reports (crowd engine).
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


# ── Neo4j Connection (Train data + Crowd Reports) ────────────────

_neo4j_driver = None


def get_neo4j_driver():
    """Get or create a Neo4j driver."""
    global _neo4j_driver
    if _neo4j_driver is None:
        from neo4j import GraphDatabase
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        _neo4j_driver = GraphDatabase.driver(uri, auth=(user, password))
        print("[core] Neo4j connected")
    return _neo4j_driver


def run_cypher(query: str, params: dict = None) -> list[dict]:
    """Execute a Cypher query and return results as list of dicts."""
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run(query, params or {})
        return [dict(record) for record in result]


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
    global _milvus_client, _neo4j_driver
    if _milvus_client:
        _milvus_client.close()
        _milvus_client = None
    if _neo4j_driver:
        _neo4j_driver.close()
        _neo4j_driver = None
    print("[core] Connections closed")
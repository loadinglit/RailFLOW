"""
RailMind Core — Shared connections for all engines.

Both Bhoomi and Dhruv import from here. Single source of truth.
Neo4j = Knowledge Graph (all engines)
Milvus = Vector store (Jan Suraksha Bot only)
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from pymilvus import connections, Collection, utility

load_dotenv()

# ── Neo4j Connection (Knowledge Graph) ─────────────────────────
# Used by: ALL 4 engines

_neo4j_driver = None


def get_neo4j_driver():
    global _neo4j_driver
    if _neo4j_driver is None:
        _neo4j_driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")),
        )
        # Verify connection
        _neo4j_driver.verify_connectivity()
        print("[core] Neo4j connected")
    return _neo4j_driver


def run_cypher(query: str, params: dict = None) -> list:
    """Run a Cypher query and return list of records as dicts."""
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run(query, params or {})
        return [record.data() for record in result]


# ── Milvus Connection (Vector Store for RAG) ───────────────────
# Used by: Engine 4 (Jan Suraksha Bot) only

_milvus_connected = False


def connect_milvus():
    global _milvus_connected
    if not _milvus_connected:
        milvus_uri = os.getenv("MILVUS_URI")
        if milvus_uri:
            # Zilliz Cloud (managed Milvus)
            connections.connect(
                alias="default",
                uri=milvus_uri,
                token=os.getenv("MILVUS_TOKEN"),
            )
        else:
            # Local Milvus
            connections.connect(
                alias="default",
                host=os.getenv("MILVUS_HOST", "localhost"),
                port=os.getenv("MILVUS_PORT", "19530"),
            )
        _milvus_connected = True
        print("[core] Milvus connected")


def get_milvus_collection(name: str) -> Collection:
    """Get a Milvus collection by name. Connect if needed."""
    connect_milvus()
    if not utility.has_collection(name):
        raise ValueError(f"Collection '{name}' does not exist in Milvus")
    collection = Collection(name)
    collection.load()
    return collection


# ── Cleanup ────────────────────────────────────────────────────

def shutdown():
    global _neo4j_driver, _milvus_connected
    if _neo4j_driver:
        _neo4j_driver.close()
        _neo4j_driver = None
    if _milvus_connected:
        connections.disconnect("default")
        _milvus_connected = False
    print("[core] All connections closed")

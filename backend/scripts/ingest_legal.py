"""
Ingest Legal Corpus into Zilliz Cloud.

Run ONCE to create the `legal_corpus` collection and upsert all chunks.
Usage: uv run python backend/scripts/ingest_legal.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.legal_corpus import LEGAL_CHUNKS
from app.core import get_milvus_client, embed_text

COLLECTION_NAME = "legal_corpus"
EMBEDDING_DIM = 1536  # text-embedding-3-small


def create_collection(client):
    """Create the legal_corpus collection with proper schema."""
    from pymilvus import CollectionSchema, FieldSchema, DataType

    if client.has_collection(COLLECTION_NAME):
        print(f"[ingest] Collection '{COLLECTION_NAME}' already exists — dropping and recreating.")
        client.drop_collection(COLLECTION_NAME)

    schema = client.create_schema(auto_id=False, enable_dynamic_field=True)
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    schema.add_field(field_name="embedding", datatype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM)
    schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=8192)
    schema.add_field(field_name="doc_type", datatype=DataType.VARCHAR, max_length=128)
    schema.add_field(field_name="incident_type", datatype=DataType.VARCHAR, max_length=128)
    schema.add_field(field_name="legal_remedy", datatype=DataType.VARCHAR, max_length=128)
    schema.add_field(field_name="authority", datatype=DataType.VARCHAR, max_length=256)
    schema.add_field(field_name="section_ref", datatype=DataType.VARCHAR, max_length=512)
    schema.add_field(field_name="compensation_eligible", datatype=DataType.BOOL)
    schema.add_field(field_name="location_scope", datatype=DataType.VARCHAR, max_length=64)

    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name="embedding",
        index_type="AUTOINDEX",
        metric_type="COSINE",
    )

    client.create_collection(
        collection_name=COLLECTION_NAME,
        schema=schema,
        index_params=index_params,
    )
    print(f"[ingest] Collection '{COLLECTION_NAME}' created.")


def ingest_chunks(client):
    """Embed and upsert all legal chunks."""
    data = []
    for i, chunk in enumerate(LEGAL_CHUNKS):
        print(f"[ingest] Embedding chunk {i + 1}/{len(LEGAL_CHUNKS)}: {chunk['section_ref'][:50]}...")
        embedding = embed_text(chunk["text"])
        data.append({
            "id": i,
            "embedding": embedding,
            "text": chunk["text"],
            "doc_type": chunk["doc_type"],
            "incident_type": chunk["incident_type"],
            "legal_remedy": chunk["legal_remedy"],
            "authority": chunk["authority"],
            "section_ref": chunk["section_ref"],
            "compensation_eligible": chunk["compensation_eligible"],
            "location_scope": chunk["location_scope"],
        })

        # Batch upsert every 20 chunks to avoid memory issues
        if len(data) >= 20:
            client.upsert(collection_name=COLLECTION_NAME, data=data)
            print(f"[ingest] Upserted batch of {len(data)} chunks.")
            data = []

    # Upsert remaining
    if data:
        client.upsert(collection_name=COLLECTION_NAME, data=data)
        print(f"[ingest] Upserted final batch of {len(data)} chunks.")

    print(f"[ingest] Done! Total chunks ingested: {len(LEGAL_CHUNKS)}")


if __name__ == "__main__":
    print("[ingest] Connecting to Zilliz Cloud...")
    client = get_milvus_client()

    print("[ingest] Creating collection...")
    create_collection(client)

    print("[ingest] Ingesting legal corpus...")
    ingest_chunks(client)

    print("[ingest] Verifying...")
    stats = client.get_collection_stats(COLLECTION_NAME)
    print(f"[ingest] Collection stats: {stats}")
    print("[ingest] All done!")
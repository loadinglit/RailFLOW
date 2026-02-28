"""
Jan Suraksha Bot — Legal Context Retrieval via Zilliz/Milvus.

3 retrieval modes:
- "identify_authority": jurisdiction_guide + helpline_directory
- "legal_basis": legal_statute + case_law + compensation_schedule
- "filing": filing_procedure + rti_template
"""

from app.core import get_milvus_client, embed_text
from app.utils.logger import get_logger

log = get_logger("jansuraksha.retrieval")

COLLECTION_NAME = "legal_corpus"

# Mode-to-filter mapping
MODE_FILTERS = {
    "identify_authority": {
        "doc_types": ["jurisdiction_guide", "helpline_directory"],
    },
    "legal_basis": {
        "doc_types": ["legal_statute", "case_law", "compensation_schedule"],
    },
    "filing": {
        "doc_types": ["filing_procedure", "rti_template"],
    },
}


def _build_filter_expr(mode: str, incident_type: str = None, location_scope: str = None) -> str:
    """Build a Milvus filter expression based on retrieval mode and optional filters."""
    conditions = []

    mode_config = MODE_FILTERS.get(mode)
    if mode_config:
        doc_types = mode_config["doc_types"]
        type_conditions = " || ".join([f'doc_type == "{dt}"' for dt in doc_types])
        conditions.append(f"({type_conditions})")

    if incident_type and incident_type != "general":
        conditions.append(f'(incident_type == "{incident_type}" || incident_type == "general")')

    if location_scope and location_scope != "national":
        conditions.append(f'(location_scope == "{location_scope}" || location_scope == "national")')

    expr = " && ".join(conditions) if conditions else ""
    return expr


def retrieve_legal_context(
    query: str,
    mode: str = "legal_basis",
    incident_type: str = None,
    location_scope: str = "mumbai",
    top_k: int = 5,
) -> list[dict]:
    """
    Retrieve relevant legal chunks from Zilliz vector store.

    Args:
        query: User's question or incident description
        mode: "identify_authority" | "legal_basis" | "filing"
        incident_type: Filter by incident type (e.g., "theft", "assault")
        location_scope: "mumbai" | "national"
        top_k: Number of results to return

    Returns:
        List of dicts with text, doc_type, section_ref, authority, etc.
    """
    log.info("Retrieving: mode=%s, incident_type=%s, scope=%s, top_k=%d",
             mode, incident_type, location_scope, top_k)
    log.debug("Query: %.100s...", query)

    client = get_milvus_client()
    log.debug("Embedding query text...")
    query_embedding = embed_text(query)
    log.debug("Embedding done (dim=%d)", len(query_embedding))

    filter_expr = _build_filter_expr(mode, incident_type, location_scope)
    log.debug("Filter expression: %s", filter_expr or "(none)")

    results = client.search(
        collection_name=COLLECTION_NAME,
        data=[query_embedding],
        limit=top_k,
        output_fields=["text", "doc_type", "incident_type", "legal_remedy",
                        "authority", "section_ref", "compensation_eligible", "location_scope"],
        filter=filter_expr if filter_expr else None,
    )

    if not results or not results[0]:
        log.warning("No results from Zilliz search")
        return []

    chunks = []
    for hit in results[0]:
        entity = hit.get("entity", {})
        chunks.append({
            "text": entity.get("text", ""),
            "doc_type": entity.get("doc_type", ""),
            "incident_type": entity.get("incident_type", ""),
            "legal_remedy": entity.get("legal_remedy", ""),
            "authority": entity.get("authority", ""),
            "section_ref": entity.get("section_ref", ""),
            "compensation_eligible": entity.get("compensation_eligible", False),
            "location_scope": entity.get("location_scope", ""),
            "score": hit.get("distance", 0.0),
        })

    log.info("Retrieved %d chunks. Top: %s (score=%.3f)",
             len(chunks),
             chunks[0]["section_ref"] if chunks else "none",
             chunks[0]["score"] if chunks else 0)

    return chunks
"""
Engine 4 — Jan Suraksha Bot Router

Agentic GraphRAG complaint filing bot.
Owner: Dhruv
"""

from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main bot endpoint.

    Flow:
    1. Pull user context from Neo4j (train, station, route)
    2. Semantic search Milvus for relevant legal sections
    3. LangGraph agent decides tools to call
    4. Return response + complaint + compensation + tracking ref

    Dhruv: Replace this stub with your LangGraph agent.
    """
    # TODO (Dhruv): Wire to LangGraph agent
    return ChatResponse(
        response=f"[stub] Received: {request.message}",
        complaint_draft=None,
        authority=None,
        compensation=None,
        cpgrams_ref=None,
        follow_up_date=None,
    )


@router.get("/user-context/{user_id}")
async def get_user_context(user_id: str):
    """
    Pull user's train/station/route context from Neo4j.

    This is how the bot skips cold-start questions —
    it already knows your train before you say anything.

    Dhruv: Use this in your LangGraph agent's first node.
    """
    from app.core import run_cypher

    results = run_cypher("""
        MATCH (u:User {user_id: $user_id})
        OPTIONAL MATCH (u)-[:HABITUALLY_TRAVELS]->(r:Route)
        OPTIONAL MATCH (r)-[:SERVED_BY]->(t:Train)
        OPTIONAL MATCH (u)-[:FILED]->(c:Complaint)
        RETURN u.name AS name,
               r.origin AS origin, r.destination AS destination,
               t.train_number AS usual_train, t.type AS train_type,
               count(c) AS previous_complaints
    """, {"user_id": user_id})

    if not results:
        return {"user_id": user_id, "context": None}
    return {"user_id": user_id, "context": results[0]}

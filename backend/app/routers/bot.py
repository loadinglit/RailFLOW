"""
Engine 4 — Jan Suraksha Bot Router

Agentic GraphRAG complaint filing bot.
Owner: Dhruv
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, ActionOption
from app.engines.jansuraksha.agent import run_agent
from app.engines.jansuraksha.neo4j_context import load_user_context
from app.utils.logger import get_logger

log = get_logger("router.bot")

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main bot endpoint.

    Flow:
    1. Pull user context from Neo4j (train, station, route)
    2. Classify incident type and intent
    3. Semantic search Milvus for relevant legal sections
    4. LangGraph agent decides tools to call
    5. Return response + complaint + compensation + tracking ref
    """
    log.info("POST /chat — user=%s, lang=%s, message=%.60s...",
             request.user_id, request.language, request.message)
    try:
        result = await run_agent(
            user_id=request.user_id,
            message=request.message,
            language=request.language,
        )
        log.info("POST /chat — SUCCESS, authority=%s, cpgrams=%s",
                 result.get("authority"), result.get("cpgrams_ref"))
        # Build options list if present (Turn 1 response)
        options_data = result.get("options")
        options = [ActionOption(**o) for o in options_data] if options_data else None

        return ChatResponse(
            response=result.get("response", "Unable to process request."),
            options=options,
            complaint_draft=result.get("complaint_draft"),
            authority=result.get("authority"),
            compensation=result.get("compensation"),
            cpgrams_ref=result.get("cpgrams_ref"),
            follow_up_date=result.get("follow_up_date"),
        )
    except Exception as e:
        log.error("POST /chat — FAILED: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Bot error: {str(e)}")


@router.get("/user-context/{user_id}")
async def get_user_context(user_id: str):
    """
    Pull user's train/station/route context from Neo4j.
    """
    log.info("GET /user-context/%s", user_id)
    try:
        ctx = load_user_context(user_id)
        if not ctx.get("found"):
            log.warning("User %s not found in Neo4j", user_id)
            return {"user_id": user_id, "context": None}
        log.info("GET /user-context/%s — found: %s", user_id, ctx.get("name"))
        return {"user_id": user_id, "context": ctx}
    except Exception as e:
        log.error("GET /user-context/%s — FAILED: %s", user_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
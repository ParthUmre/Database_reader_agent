from unittest import result

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from uuid import uuid4
from typing import Optional

from app.agents.memory.conversation_memory import (
    add_message
)

from sqlalchemy.orm import Session

from app.database.mysql.connection import get_db

from app.agents.orchestrator.router import (
    route_user_query
)

from app.core.logging import get_logger


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# ROUTER
# ==========================================
router = APIRouter(
    prefix="/chat",
    tags=["AI Chat"]
)


# ==========================================
# REQUEST SCHEMA
# ==========================================
class ChatRequest(BaseModel):

    query: str

    session_id: Optional[str] = None


# ==========================================
# RESPONSE SCHEMA
# ==========================================
class ChatResponse(BaseModel):

    success: bool

    session_id: str | None = None

    query_type: str | None = None

    response: dict | list | str | None = None

    sql: str | None = None

    tables: list | None = None

    error: str | None = None


# ==========================================
# AI QUERY ENDPOINT
# ==========================================
@router.post(
    "/query",
    response_model=ChatResponse
)
def query_ai_system(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    try:

        # ==============================
        # SESSION MANAGEMENT
        # ==============================
        session_id = (
            request.session_id
            if request.session_id
            else str(uuid4())
        )

        logger.info(
            f"AI query received for session "
            f"{session_id}: {request.query}"
        )

        # ==============================
        # STORE USER MESSAGE
        # ==============================
        add_message(
            session_id=session_id,
            role="user",
            message=request.query
        )

        # ==============================
        # ROUTE QUERY
        # ==============================
        result = route_user_query(
            db=db,
            user_query=request.query
        )

        # ==============================
        # STORE ASSISTANT RESPONSE
        # ==============================
        add_message(
            session_id=session_id,
            role="assistant",
            message=str(result)
        )

        logger.info(
            "AI query processed successfully."
        )

        # ==============================
        # FINAL RESPONSE
        # ==============================
        logger.info(
    "AI query processed successfully."
)

        print("FINAL RESULT:", result)

        agent_response = result.get("response", {})

        return {
    "success": result.get("success", False),

    "session_id": session_id,

    "query_type": result.get("query_type", "SQL"),

    "response": agent_response.get("data"),

    "sql": agent_response.get("generated_sql"),

    "tables": [],

    "error": result.get("error")
}
    except Exception as e:

        logger.error(
            f"AI query endpoint failed: {e}"
        )

        return {
            "success": False,
            "error": str(e)
        }
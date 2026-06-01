from uuid import uuid4
from typing import Optional, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.database.mysql.connection import get_db

from app.agents.memory.conversation_memory import (
    add_message
)

from app.agents.orchestrator.router import (
    route_user_query
)

from app.services.store_context_service import (
    validate_store_context
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

    store_code: Optional[str] = None


# ==========================================
# RESPONSE SCHEMA
# ==========================================
class ChatResponse(BaseModel):

    success: bool

    session_id: Optional[str] = None

    query_type: Optional[str] = None

    response: Optional[Any] = None

    error: Optional[str] = None


# ==========================================
# NORMALIZE RESPONSE FOR FRONTEND
# ==========================================
def build_user_facing_response(
    agent_result: dict
):

    """
    This removes developer-only fields like generated_sql
    and returns only business-facing output.
    """

    if not agent_result:

        return {
            "message": "No response generated."
        }

    agent_response = agent_result.get(
        "response",
        agent_result
    )

    # Sometimes router returns:
    # {
    #   success: True,
    #   query_type: SQL,
    #   response: {
    #       success: True,
    #       data: [...],
    #       generated_sql: "..."
    #   }
    # }

    if isinstance(agent_response, dict):

        return {
            "answer": (
                agent_response.get("business_response")
                or agent_response.get("answer")
                or agent_response.get("insight")
                or agent_response.get("message")
            ),

            "data": agent_response.get("data"),

            "row_count": agent_response.get("row_count"),

            "analytics_type": agent_response.get("analytics_type")
        }

    return agent_response


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
            f"AI query received | "
            f"session_id={session_id} | "
            f"store_code={request.store_code} | "
            f"query={request.query}"
        )

        # ==============================
        # STORE CODE REQUIRED
        # ==============================
        if not request.store_code:

            return {
                "success": False,
                "session_id": session_id,
                "error": "Store code is required. Please enter your store code."
            }

        # ==============================
        # RESOLVE STORE CODE → RETAILER ID
        # ==============================
        store_context = validate_store_context(
            db=db,
            store_code=request.store_code
        )

        if not store_context["success"]:

            return {
                "success": False,
                "session_id": session_id,
                "error": store_context["error"]
            }

        retailer_id = store_context["retailer_id"]

        logger.info(
            f"Resolved store_code={request.store_code} "
            f"to retailer_id={retailer_id}"
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
            user_query=request.query,
            session_id=session_id,
            store_code=request.store_code,
            retailer_id=retailer_id
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

        user_response = build_user_facing_response(
            result
        )

        # ==============================
        # FINAL RESPONSE
        # ==============================
        return {
            "success": result.get(
                "success",
                False
            ),

            "session_id": session_id,

            "query_type": result.get(
                "query_type",
                "SQL"
            ),

            "response": user_response,

            "error": result.get(
                "error"
            )
        }

    except Exception as e:

        logger.error(
            f"AI query endpoint failed: {e}"
        )

        return {
            "success": False,
            "error": str(e)
        }
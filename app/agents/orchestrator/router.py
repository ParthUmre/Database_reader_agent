from sqlalchemy.orm import Session

from app.core.logging import get_logger

from app.agents.sql_agents.query_classifier import (
    classify_query
)

from app.agents.sql_agents.sql_pipeline import (
    run_sql_pipeline
)

from app.agents.rag_agent.rag_pipeline import (
    run_rag_pipeline
)

# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# MAIN QUERY ROUTER
# ==========================================
def route_user_query(
    db: Session,
    user_query: str
):

    try:

        logger.info(
            f"Routing user query: {user_query}"
        )

        # ==================================
        # STEP 1: CLASSIFY QUERY
        # ==================================
        query_type = classify_query(
            user_query
        )

        logger.info(
            f"Detected query type: {query_type}"
        )

        # ==================================
        # STEP 2: ROUTE QUERY
        # ==================================

        # ----------------------------------
        # SQL ROUTE
        # ----------------------------------
        if query_type == "SQL":

            logger.info(
                "Routing to SQL Agent."
            )

            result = run_sql_pipeline(
                db=db,
                user_query=user_query
            )

            return {
                "success": result.get("success", False),
                "query_type": "SQL",
                "response": result,
                "error": result.get("error")
            }

        # ----------------------------------
        # RAG ROUTE
        # ----------------------------------
        elif query_type == "RAG":

            logger.info(
                "Routing to RAG pipeline."
            )

            result = run_rag_pipeline(
                user_query
            )

            return result

        # ----------------------------------
        # ANALYTICS ROUTE
        # ----------------------------------
        elif query_type == "ANALYTICS":

            logger.info(
                "Routing to Analytics Agent."
            )

            return {
                "success": True,
                "query_type": "ANALYTICS",
                "response": (
                    "Analytics pipeline "
                    "not implemented yet."
                )
            }

        # ----------------------------------
        # PREDICTIVE ROUTE
        # ----------------------------------
        elif query_type == "PREDICTIVE":

            logger.info(
                "Routing to Predictive Agent."
            )

            return {
                "success": True,
                "query_type": "PREDICTIVE",
                "response": (
                    "Predictive pipeline "
                    "not implemented yet."
                )
            }

        # ----------------------------------
        # FALLBACK
        # ----------------------------------
        return {
            "success": False,
            "error": "Unsupported query type."
        }

    except Exception as e:

        logger.error(
            f"Query routing failed: {e}"
        )

        return {
            "success": False,
            "error": str(e)
        }

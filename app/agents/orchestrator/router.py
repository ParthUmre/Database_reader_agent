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

#from app.agents.analytics_agent.analytics_pipeline import (
#    run_analytics_pipeline
#)


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# MAIN QUERY ROUTER
# ==========================================
def route_user_query(
    db: Session,
    user_query: str,
    session_id: str | None = None,
    store_code: str | None = None,
    retailer_id: int | None = None
):

    try:

        logger.info(
            f"Routing user query: {user_query}"
        )

        logger.info(
            f"Context | session_id={session_id} | "
            f"store_code={store_code} | retailer_id={retailer_id}"
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
                user_query=user_query,
                session_id=session_id,
                retailer_id=retailer_id
            )

            return {
                "success": result.get(
                    "success",
                    False
                ),

                "query_type": "SQL",

                "response": result,

                "error": result.get(
                    "error"
                )
            }

        # ----------------------------------
        # RAG ROUTE
        # ----------------------------------
        elif query_type == "RAG":

            logger.info(
                "Routing to RAG pipeline."
            )

            result = run_rag_pipeline(
                user_query=user_query
            )

            return {
                "success": result.get(
                    "success",
                    False
                ),

                "query_type": "RAG",

                "response": result,

                "error": result.get(
                    "error"
                )
            }

        # ----------------------------------
        # ANALYTICS ROUTE
        # ----------------------------------
        elif query_type == "ANALYTICS":

            logger.info(
                "Routing to Analytics Agent."
            )

            #result = run_analytics_pipeline(
            #    db=db,
            #    user_query=user_query,
            #    retailer_id=retailer_id
            #)

            return {
                "success": result.get(
                    "success",
                    False
                ),

                "query_type": "ANALYTICS",

                "response": result,

                "error": result.get(
                    "error"
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

                "response": {
                    "message": (
                        "Predictive Agent is connected, "
                        "but forecasting logic is not implemented yet."
                    ),

                    "future_scope": [
                        "Demand forecasting",
                        "Stock-out risk prediction",
                        "Sales trend prediction",
                        "Inventory reorder recommendation"
                    ]
                },

                "error": None
            }

        # ----------------------------------
        # FALLBACK
        # ----------------------------------
        logger.warning(
            f"Unsupported query type: {query_type}"
        )

        return {
            "success": False,
            "query_type": query_type,
            "response": None,
            "error": "Unsupported query type."
        }

    except Exception as e:

        logger.error(
            f"Query routing failed: {e}"
        )

        return {
            "success": False,
            "query_type": None,
            "response": None,
            "error": str(e)
        }
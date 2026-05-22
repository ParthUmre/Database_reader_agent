from app.core.logging import get_logger

from app.langgraph.state.graph_state import (
    GraphState
)


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# ROUTING EDGE
# ==========================================
def route_query(
    state: GraphState
):

    try:

        logger.info(
            "Evaluating routing edge."
        )

        # ==================================
        # FETCH QUERY TYPE
        # ==================================
        query_type = state.get(
            "query_type",
            "SQL"
        )

        logger.info(
            f"Routing query type: "
            f"{query_type}"
        )

        # ==================================
        # VALID ROUTES
        # ==================================
        valid_routes = [

            "SQL",

            "RAG",

            "ANALYTICS",

            "PREDICTIVE"
        ]

        # ==================================
        # FALLBACK ROUTE
        # ==================================
        if query_type not in valid_routes:

            logger.warning(
                f"Unknown route: {query_type}. "
                f"Defaulting to SQL."
            )

            return "SQL"

        return query_type

    except Exception as e:

        logger.error(
            f"Routing edge failed: {e}"
        )

        return "SQL"
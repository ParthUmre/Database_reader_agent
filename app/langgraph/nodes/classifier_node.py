from app.core.logging import get_logger

from app.langgraph.state.graph_state import (
    GraphState
)

from app.agents.sql_agents.query_classifier import (
    classify_query
)


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# CLASSIFIER NODE
# ==========================================
def classifier_node(
    state: GraphState
):

    try:

        logger.info(
            "Executing classifier node."
        )

        # ==================================
        # FETCH USER QUERY
        # ==================================
        user_query = state.get(
            "user_query",
            ""
        )

        # ==================================
        # CLASSIFY QUERY
        # ==================================
        query_type = classify_query(
            user_query
        )

        logger.info(
            f"Query classified as: "
            f"{query_type}"
        )

        # ==================================
        # TRACK VISITED NODES
        # ==================================
        visited_nodes = state.get(
            "visited_nodes",
            []
        )

        visited_nodes.append(
            "classifier_node"
        )

        # ==================================
        # UPDATE STATE
        # ==================================
        updated_state = {

            **state,

            "query_type": query_type,

            "visited_nodes": visited_nodes
        }

        return updated_state

    except Exception as e:

        logger.error(
            f"Classifier node failed: {e}"
        )

        return {

            **state,

            "success": False,

            "error": str(e)
        }
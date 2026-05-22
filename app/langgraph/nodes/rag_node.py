from app.core.logging import get_logger

from app.langgraph.state.graph_state import (
    GraphState
)

from app.agents.rag_agent.rag_pipeline import (
    run_rag_pipeline
)


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# RAG NODE
# ==========================================
def rag_node(
    state: GraphState
):

    try:

        logger.info(
            "Executing RAG node."
        )

        # ==================================
        # FETCH STATE DATA
        # ==================================
        user_query = state.get(
            "user_query",
            ""
        )

        # ==================================
        # RUN RAG PIPELINE
        # ==================================
        result = run_rag_pipeline(
            user_query=user_query
        )

        logger.info(
            "RAG pipeline executed successfully."
        )

        # ==================================
        # TRACK VISITED NODES
        # ==================================
        visited_nodes = state.get(
            "visited_nodes",
            []
        )

        visited_nodes.append(
            "rag_node"
        )

        # ==================================
        # UPDATE STATE
        # ==================================
        updated_state = {

            **state,

            "success": result.get(
                "success",
                False
            ),

            "rag_answer": result.get(
                "answer"
            ),

            "rag_context": result.get(
                "sources"
            ),

            "final_response": result,

            "visited_nodes": visited_nodes
        }

        return updated_state

    except Exception as e:

        logger.error(
            f"RAG node failed: {e}"
        )

        return {

            **state,

            "success": False,

            "error": str(e)
        }
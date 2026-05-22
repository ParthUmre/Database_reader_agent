from time import time

from app.core.logging import get_logger

from app.langgraph.graph_builder import (
    build_agentic_graph
)

from app.langgraph.state.graph_state import (
    GraphState
)


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# BUILD GRAPH ON STARTUP
# ==========================================
graph = build_agentic_graph()


# ==========================================
# RUN LANGGRAPH WORKFLOW
# ==========================================
def run_agentic_workflow(

    user_query: str,

    session_id: str
):

    start_time = time()

    try:

        logger.info(
            "Starting LangGraph workflow execution."
        )

        # ==================================
        # INITIAL GRAPH STATE
        # ==================================
        initial_state: GraphState = {

            "user_query": user_query,

            "session_id": session_id,

            "visited_nodes": [],

            "success": True
        }

        # ==================================
        # EXECUTE GRAPH
        # ==================================
        result = graph.invoke(
            initial_state
        )

        execution_time = (
            time() - start_time
        )

        logger.info(
            f"Workflow completed in "
            f"{execution_time:.2f} seconds."
        )

        # ==================================
        # FINAL RESPONSE
        # ==================================
        return {

            "success": result.get(
                "success",
                False
            ),

            "query_type": result.get(
                "query_type"
            ),

            "response": result.get(
                "final_response"
            ),

            "visited_nodes": result.get(
                "visited_nodes",
                []
            ),

            "execution_time": (
                execution_time
            )
        }

    except Exception as e:

        logger.error(
            f"Graph workflow failed: {e}"
        )

        return {

            "success": False,

            "error": str(e)
        }
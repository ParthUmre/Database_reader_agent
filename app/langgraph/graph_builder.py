from langgraph.graph import (
    StateGraph,
    END
)

from app.core.logging import get_logger

from app.langgraph.state.graph_state import (
    GraphState
)

from app.langgraph.nodes.classifier_node import (
    classifier_node
)

from app.langgraph.nodes.sql_node import (
    sql_node
)

from app.langgraph.nodes.rag_node import (
    rag_node
)

#from app.langgraph.nodes.analytics_node import (
#   analytics_node
#)

#from app.langgraph.nodes.predictive_node import (
#    predictive_node
#)

from app.langgraph.edges.routing_edges import (
    route_query
)


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# BUILD LANGGRAPH
# ==========================================
def build_agentic_graph():

    try:

        logger.info(
            "Building enterprise LangGraph workflow."
        )

        # ==================================
        # INITIALIZE GRAPH
        # ==================================
        workflow = StateGraph(
            GraphState
        )

        # ==================================
        # ADD NODES
        # ==================================
        workflow.add_node(
            "classifier",
            classifier_node
        )

        workflow.add_node(
            "sql_agent",
            sql_node
        )

        workflow.add_node(
            "rag_agent",
            rag_node
        )

        #workflow.add_node(
         #   "analytics_agent",
          #  analytics_node
        #)

        #workflow.add_node(
         #   "predictive_agent",
          #  predictive_node
        #)

        # ==================================
        # ENTRY POINT
        # ==================================
        workflow.set_entry_point(
            "classifier"
        )

        # ==================================
        # CONDITIONAL ROUTING
        # ==================================
        workflow.add_conditional_edges(

            "classifier",

            route_query,

            {

                "SQL": "sql_agent",

                "RAG": "rag_agent",

                "ANALYTICS": (
                    "analytics_agent"
                ),

                "PREDICTIVE": (
                    "predictive_agent"
                )
            }
        )

        # ==================================
        # TERMINATION EDGES
        # ==================================
        workflow.add_edge(
            "sql_agent",
            END
        )

        workflow.add_edge(
            "rag_agent",
            END
        )

        workflow.add_edge(
            "analytics_agent",
            END
        )

        workflow.add_edge(
            "predictive_agent",
            END
        )

        # ==================================
        # COMPILE GRAPH
        # ==================================
        compiled_graph = workflow.compile()

        logger.info(
            "LangGraph workflow compiled successfully."
        )

        return compiled_graph

    except Exception as e:

        logger.error(
            f"LangGraph build failed: {e}"
        )

        raise e
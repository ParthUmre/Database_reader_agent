from typing import TypedDict
from typing import Optional
from typing import List
from typing import Dict
from typing import Any


# ==========================================
# GRAPH STATE
# ==========================================
class GraphState(TypedDict, total=False):

    # ======================================
    # USER INPUT
    # ======================================
    user_query: str

    session_id: str

    # ======================================
    # QUERY CLASSIFICATION
    # ======================================
    query_type: str

    # ======================================
    # SQL AGENT DATA
    # ======================================
    generated_sql: str

    sql_result: Dict[str, Any]

    # ======================================
    # RAG AGENT DATA
    # ======================================
    rag_context: List[Dict[str, Any]]

    rag_answer: str

    # ======================================
    # ANALYTICS AGENT DATA
    # ======================================
    analytics_result: Dict[str, Any]

    # ======================================
    # PREDICTIVE AGENT DATA
    # ======================================
    prediction_result: Dict[str, Any]

    # ======================================
    # FINAL RESPONSE
    # ======================================
    final_response: Dict[str, Any]

    # ======================================
    # EXECUTION METADATA
    # ======================================
    success: bool

    error: str

    execution_time: float

    tokens_used: int

    # ======================================
    # MEMORY
    # ======================================
    conversation_history: str

    # ======================================
    # OBSERVABILITY
    # ======================================
    visited_nodes: List[str]
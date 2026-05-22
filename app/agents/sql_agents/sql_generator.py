from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings
from app.core.logging import get_logger

from app.vectorstore.search import semantic_search

from app.agents.memory.conversation_memory import (
    format_conversation_history
)

from app.database.mysql.connection import (
    engine
)

from app.agents.sql_agents.schema_context import (
    generate_schema_context
)

from app.prompts.sql.system_prompts import (
    SQL_SYSTEM_PROMPT
)


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# LLM INITIALIZATION
# ==========================================


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=settings.GEMINI_API_KEY,
    max_tokens=300,  # Replaced max_new_tokens
    temperature=0.1
)

# ==========================================
# DATABASE SCHEMA CONTEXT
# ==========================================
from app.database.mysql.connection import (
    engine
)

from app.agents.sql_agents.schema_context import (
    generate_schema_context
)


from app.prompts.sql.system_prompts import (
    SQL_SYSTEM_PROMPT   
)

# ==========================================
# SQL GENERATION PROMPT
# ==========================================

# ==================================
# MEMORY CONTEXT
# =================================
# ==========================================
# GENERATE SQL QUERY
# ==========================================
def generate_sql_query(
    user_query: str,
    session_id: str | None = None
    
):

    try:

        logger.info(
            f"Generating SQL for query: {user_query}"
        )

        # ==================================
        # RETRIEVE SEMANTIC CONTEXT
        # ==================================
        rag_results = semantic_search(
            user_query,
            limit=3
        )

        context = "\n".join([
            result["text"]
            for result in rag_results
        ])

        # ==================================
        # BUILD FINAL PROMPT
        # ==================================
        final_prompt = SQL_SYSTEM_PROMPT.format(
            schema=generate_schema_context(engine),
            context=context,
            question=user_query,
        )
        
        # ==================================
        # GENERATE SQL
        # ==================================
        response = llm.invoke(final_prompt)

        sql_query = response.content.strip()

        logger.info(
            f"Generated SQL: {sql_query}"
        )

        return sql_query

    except Exception as e:

        logger.error(
            f"SQL generation failed: {e}"
        )

        raise e
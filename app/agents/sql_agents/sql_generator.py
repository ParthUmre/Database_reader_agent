from langchain_google_genai import ChatGoogleGenerativeAI

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
    temperature=0.1,
    max_tokens=400
)


# ==========================================
# CLEAN SQL OUTPUT
# ==========================================
def clean_sql_output(
    response_text: str
):

    if not response_text:

        return ""

    sql = response_text.strip()

    # ======================================
    # REMOVE MARKDOWN CODE BLOCKS
    # ======================================
    sql = sql.replace("```sql", "")
    sql = sql.replace("```SQL", "")
    sql = sql.replace("```", "")

    sql = sql.strip()

    # ======================================
    # REMOVE COMMON PREFIXES
    # ======================================
    prefixes = [
        "SQL:",
        "SQL QUERY:",
        "QUERY:",
        "Here is the SQL query:",
        "Here is the query:",
        "The SQL query is:"
    ]

    for prefix in prefixes:

        if sql.upper().startswith(
            prefix.upper()
        ):

            sql = sql[len(prefix):].strip()

    # ======================================
    # KEEP ONLY FIRST SQL STATEMENT
    # ======================================
    if ";" in sql:

        sql = sql.split(";")[0].strip() + ";"

    else:

        sql = sql.strip() + ";"

    return sql


# ==========================================
# GENERATE SQL QUERY
# ==========================================
def generate_sql_query(
    user_query: str,
    session_id: str | None = None,
    retailer_id: int | None = None
):

    try:

        logger.info(
            f"Generating SQL for query: {user_query}"
        )

        logger.info(
            f"SQL generator retailer_id: {retailer_id}"
        )

        # ==================================
        # RETAILER ID IS REQUIRED
        # ==================================
        if retailer_id is None:

            raise ValueError(
                "retailer_id is required for SQL generation."
            )

        # ==================================
        # MEMORY CONTEXT
        # ==================================
        conversation_history = ""

        if session_id:

            conversation_history = (
                format_conversation_history(
                    session_id
                )
            )

        # ==================================
        # SEMANTIC CONTEXT
        # ==================================
        rag_results = semantic_search(
            user_query,
            limit=3
        )

        semantic_context = "\n".join([

            result.get("text", "")

            for result in rag_results
        ])

        # ==================================
        # COMBINED CONTEXT
        # ==================================
        context = f"""
==================================================
CONVERSATION HISTORY
==================================================

{conversation_history}

==================================================
SEMANTIC CONTEXT
==================================================

{semantic_context}
"""

        # ==================================
        # DYNAMIC DATABASE SCHEMA
        # ==================================
        schema_context = generate_schema_context(
            engine
        )

        # ==================================
        # BUILD FINAL PROMPT
        # ==================================
        final_prompt = SQL_SYSTEM_PROMPT.format(
            schema=schema_context,
            context=context,
            question=user_query,
            retailer_id=retailer_id
        )

        logger.info(
            "Final SQL prompt generated successfully."
        )

        # ==================================
        # GENERATE SQL USING GEMINI
        # ==================================
        response = llm.invoke(
            final_prompt
        )

        sql_query = clean_sql_output(
            response.content
        )

        logger.info(
            f"Generated SQL: {sql_query}"
        )

        return sql_query

    except Exception as e:

        logger.error(
            f"SQL generation failed: {e}"
        )

        raise e
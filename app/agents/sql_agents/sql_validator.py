import re

from app.core.logging import get_logger


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# BLOCKED SQL KEYWORDS
# ==========================================
BLOCKED_KEYWORDS = [
    "DELETE",
    "DROP",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "REPLACE",
    "GRANT",
    "REVOKE"
]


# ==========================================
# ALLOWED SQL STARTERS
# ==========================================
ALLOWED_STARTERS = [
    "SELECT",
    "WITH"
]


# ==========================================
# VALIDATE SQL QUERY
# ==========================================
def validate_sql_query(
    sql_query: str
):

    try:

        logger.info(
            "Validating generated SQL query."
        )

        cleaned_query = sql_query.strip().upper()

        # ==================================
        # CHECK QUERY START
        # ==================================
        if not any(
            cleaned_query.startswith(keyword)
            for keyword in ALLOWED_STARTERS
        ):

            logger.warning(
                "Query does not start with allowed SQL keyword."
            )

            return False, (
                "Only SELECT queries are allowed."
            )

        # ==================================
        # CHECK BLOCKED KEYWORDS
        # ==================================
        for keyword in BLOCKED_KEYWORDS:

            pattern = rf"\b{keyword}\b"

            if re.search(pattern, cleaned_query):

                logger.warning(
                    f"Blocked keyword detected: {keyword}"
                )

                return False, (
                    f"Blocked SQL keyword detected: {keyword}"
                )

        # ==================================
        # CHECK MULTIPLE STATEMENTS
        # ==================================
        statements = [
            stmt.strip()
            for stmt in cleaned_query.split(";")
            if stmt.strip()
        ]

        if len(statements) > 1:

            logger.warning(
                "Multiple SQL statements detected."
            )

            return False, (
                "Multiple SQL statements are not allowed."
            )

        # ==================================
        # CHECK COMMENT INJECTION
        # ==================================
        if "--" in cleaned_query or "/*" in cleaned_query:

            logger.warning(
                "SQL comment injection detected."
            )

            return False, (
                "SQL comments are not allowed."
            )

        logger.info(
            "SQL validation successful."
        )

        return True, "SQL query is valid."

    except Exception as e:

        logger.error(
            f"SQL validation failed: {e}"
        )

        return False, str(e)
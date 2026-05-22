from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logging import get_logger


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# EXECUTE SQL QUERY
# ==========================================
def execute_sql_query(
    db: Session,
    sql_query: str
):

    try:

        logger.info(
            f"Executing SQL query: {sql_query}"
        )

        # ==================================
        # EXECUTE QUERY
        # ==================================
        result = db.execute(
            text(sql_query)
        )

        # ==================================
        # FETCH RESULTS
        # ==================================
        rows = result.fetchall()

        # ==================================
        # COLUMN NAMES
        # ==================================
        columns = result.keys()

        # ==================================
        # FORMAT RESULTS
        # ==================================
        formatted_results = []

        for row in rows:

            formatted_results.append(
                dict(zip(columns, row))
            )

        logger.info(
            f"Query executed successfully. "
            f"Rows fetched: {len(formatted_results)}"
        )

        return {
            "success": True,
            "row_count": len(formatted_results),
            "data": formatted_results
        }

    except Exception as e:

        logger.error(
            f"SQL execution failed: {e}"
        )

        return {
            "success": False,
            "error": str(e)
        }
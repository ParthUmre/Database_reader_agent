from sqlalchemy.orm import Session

from app.core.logging import get_logger

from app.agents.sql_agents.sql_generator import (
    generate_sql_query
)

from app.agents.sql_agents.sql_validator import (
    validate_sql_query
)

from app.agents.sql_agents.sql_executor import (
    execute_sql_query
)


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# COMPLETE SQL PIPELINE
# ==========================================
def run_sql_pipeline(
    db: Session,
    user_query: str
):

    try:

        logger.info(
            f"Starting SQL pipeline for query: "
            f"{user_query}"
        )

        # ==================================
        # STEP 1: GENERATE SQL
        # ==================================
        generated_sql = generate_sql_query(
            user_query
        )

        logger.info(
            f"Generated SQL: {generated_sql}"
        )

        # ==================================
        # STEP 2: VALIDATE SQL
        # ==================================
        is_valid, validation_message = (
            validate_sql_query(
                generated_sql
            )
        )

        if not is_valid:

            logger.warning(
                f"SQL validation failed: "
                f"{validation_message}"
            )

            return {
                "success": False,
                "stage": "validation",
                "error": validation_message
            }

        logger.info(
            "SQL validation successful."
        )

        # ==================================
        # STEP 3: EXECUTE SQL
        # ==================================
        execution_result = execute_sql_query(
            db,
            generated_sql
        )

        if not execution_result["success"]:

            logger.error(
                f"SQL execution failed: "
                f"{execution_result['error']}"
            )

            return {
                "success": False,
                "stage": "execution",
                "error": execution_result["error"]
            }

        logger.info(
            "SQL pipeline completed successfully."
        )

        # ==================================
        # FINAL RESPONSE
        # ==================================
        return {
            "success": True,
            "user_query": user_query,
            "generated_sql": generated_sql,
            "row_count": execution_result[
                "row_count"
            ],
            "data": execution_result["data"]
        }

    except Exception as e:

        logger.error(
            f"SQL pipeline failed: {e}"
        )

        return {
            "success": False,
            "stage": "pipeline",
            "error": str(e)
        }
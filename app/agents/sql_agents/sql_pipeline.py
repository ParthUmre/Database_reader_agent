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
    user_query: str,
    session_id: str | None = None,
    retailer_id: int | None = None
):

    try:

        logger.info(
            f"Starting SQL pipeline for query: {user_query}"
        )

        logger.info(
            f"SQL pipeline retailer_id: {retailer_id}"
        )

        # ==================================
        # RETAILER CHECK
        # ==================================
        if retailer_id is None:

            return {
                "success": False,
                "query_type": "SQL",
                "stage": "retailer_context",
                "error": "Retailer context is missing. Store code must be resolved first."
            }

        # ==================================
        # STEP 1: GENERATE SQL
        # ==================================
        generated_sql = generate_sql_query(
            user_query=user_query,
            session_id=session_id,
            retailer_id=retailer_id
        )

        logger.info(
            f"Generated SQL: {generated_sql}"
        )

        # ==================================
        # STEP 2: VALIDATE SQL
        # ==================================
        is_valid, validation_message = validate_sql_query(
            generated_sql
        )

        if not is_valid:

            logger.warning(
                f"SQL validation failed: {validation_message}"
            )

            return {
                "success": False,
                "query_type": "SQL",
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
            db=db,
            sql_query=generated_sql
        )

        if not execution_result.get("success"):

            logger.error(
                f"SQL execution failed: {execution_result.get('error')}"
            )

            return {
                "success": False,
                "query_type": "SQL",
                "stage": "execution",
                "error": execution_result.get("error")
            }

        data = execution_result.get(
            "data",
            []
        )

        row_count = execution_result.get(
            "row_count",
            0
        )

        # ==================================
        # STEP 4: BUSINESS RESPONSE
        # ==================================
        business_response = build_business_response(
            user_query=user_query,
            data=data
        )

        logger.info(
            "SQL pipeline completed successfully."
        )

        # ==================================
        # FINAL RESPONSE
        # ==================================
        return {
            "success": True,
            "query_type": "SQL",
            "user_query": user_query,
            "business_response": business_response,
            "row_count": row_count,
            "data": data,

            # Keep internally useful.
            # Frontend/chat.py should not show this to normal users.
            "generated_sql": generated_sql
        }

    except Exception as e:

        logger.error(
            f"SQL pipeline failed: {e}"
        )

        return {
            "success": False,
            "query_type": "SQL",
            "stage": "pipeline",
            "error": str(e)
        }


# ==========================================
# BUSINESS RESPONSE FORMATTER
# ==========================================
def build_business_response(
    user_query: str,
    data: list
):

    if not data:

        return (
            "I could not find any matching records for your store."
        )

    # ======================================
    # SINGLE AGGREGATE RESULT
    # Example:
    # [{"total_sales": 50000}]
    # [{"average_tax": 191.88}]
    # ======================================
    if (
        len(data) == 1
        and isinstance(data[0], dict)
        and len(data[0].keys()) == 1
    ):

        key = list(data[0].keys())[0]

        value = data[0][key]

        readable_key = key.replace(
            "_",
            " "
        ).title()

        return (
            f"{readable_key} for your store is {value}."
        )

    # ======================================
    # SINGLE ROW MULTIPLE VALUES
    # ======================================
    if len(data) == 1 and isinstance(data[0], dict):

        lines = []

        for key, value in data[0].items():

            readable_key = key.replace(
                "_",
                " "
            ).title()

            lines.append(
                f"{readable_key}: {value}"
            )

        return (
            "Here is the result for your store:\n\n"
            + "\n".join(lines)
        )

    # ======================================
    # MULTIPLE ROWS
    # ======================================
    preview_count = min(
        len(data),
        5
    )

    return (
        f"I found {len(data)} matching records for your store. "
        f"Showing the first {preview_count} records below."
    )
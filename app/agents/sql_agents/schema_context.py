from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from app.core.logging import get_logger


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# GENERATE SCHEMA CONTEXT
# ==========================================
def generate_schema_context(
    engine: Engine
):

    try:

        logger.info(
            "Generating dynamic schema context."
        )

        inspector = inspect(engine)

        tables = inspector.get_table_names()

        schema_context = []

        # ==================================
        # PROCESS TABLES
        # ==================================
        for table in tables:

            schema_context.append(
                f"TABLE: {table}"
            )

            # ==============================
            # COLUMNS
            # ==============================
            columns = inspector.get_columns(table)

            for column in columns:

                column_name = column["name"]

                column_type = str(
                    column["type"]
                )

                schema_context.append(
                    f"- {column_name} ({column_type})"
                )

            schema_context.append("")

            # ==============================
            # FOREIGN KEYS
            # ==============================
            foreign_keys = inspector.get_foreign_keys(
                table
            )

            if foreign_keys:

                schema_context.append(
                    "RELATIONSHIPS:"
                )

                for fk in foreign_keys:

                    constrained_columns = (
                        fk["constrained_columns"]
                    )

                    referred_table = (
                        fk["referred_table"]
                    )

                    referred_columns = (
                        fk["referred_columns"]
                    )

                    relationship = (
                        f"- "
                        f"{table}."
                        f"{constrained_columns[0]}"
                        f" -> "
                        f"{referred_table}."
                        f"{referred_columns[0]}"
                    )

                    schema_context.append(
                        relationship
                    )

            schema_context.append(
                "\n"
            )

        final_schema = "\n".join(
            schema_context
        )

        logger.info(
            "Dynamic schema context generated successfully."
        )

        return final_schema

    except Exception as e:

        logger.error(
            f"Schema context generation failed: {e}"
        )

        raise e
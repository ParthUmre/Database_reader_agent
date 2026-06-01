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
# TABLES THAT SHOULD BE RETAILER FILTERED
# ==========================================
RETAILER_FILTER_TABLES = [
    "gpos_sales",
    "gpos_salesb2b",
    "gpos_invsummary_item",
    "gpos_item_quantities",
    "finance_transactions"
]


# ==========================================
# TABLES WHERE RETAILER FILTER IS OPTIONAL
# ==========================================
RETAILER_MASTER_TABLES = [
    "gpos_retailer"
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

        if not sql_query:

            return False, "SQL query is empty."

        raw_query = sql_query.strip()

        cleaned_query = raw_query.upper()

        # ==================================
        # CHECK QUERY START
        # ==================================
        if not any(
            cleaned_query.startswith(keyword)
            for keyword in ALLOWED_STARTERS
        ):

            logger.warning(
                "Query does not start with SELECT or WITH."
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
                    f"Blocked SQL keyword detected: {keyword}"
                )

                return False, (
                    f"Blocked SQL keyword detected: {keyword}"
                )

        # ==================================
        # CHECK MULTIPLE STATEMENTS
        # ==================================
        statements = [
            stmt.strip()
            for stmt in raw_query.split(";")
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
        if (
            "--" in raw_query
            or "/*" in raw_query
            or "*/" in raw_query
        ):

            logger.warning(
                "SQL comment detected."
            )

            return False, (
                "SQL comments are not allowed."
            )

        # ==================================
        # BLOCK TABLE ALIASES
        # ==================================
        alias_valid, alias_message = check_no_table_aliases(
            raw_query
        )

        if not alias_valid:

            return False, alias_message

        # ==================================
        # FORCE RETAILER FILTER
        # ==================================
        retailer_valid, retailer_message = (
            check_retailer_filter(raw_query)
        )

        if not retailer_valid:

            return False, retailer_message

        logger.info(
            "SQL validation successful."
        )

        return True, "SQL query is valid."

    except Exception as e:

        logger.error(
            f"SQL validation failed: {e}"
        )

        return False, str(e)


# ==========================================
# CHECK NO TABLE ALIASES
# ==========================================
def check_no_table_aliases(
    sql_query: str
):

    """
    Blocks SQL like:
    FROM gpos_sales gs
    FROM gpos_sales AS gs
    JOIN gpos_items gi
    JOIN gpos_items AS gi

    Allows:
    FROM gpos_sales
    JOIN gpos_items
    """

    try:

        query = normalize_spaces(
            sql_query
        )

        # ----------------------------------
        # Block FROM table AS alias
        # ----------------------------------
        from_as_alias = (
            r"\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+AS\s+([a-zA-Z_][a-zA-Z0-9_]*)"
        )

        if re.search(
            from_as_alias,
            query,
            flags=re.IGNORECASE
        ):

            logger.warning(
                "Table alias detected using AS after FROM."
            )

            return False, (
                "Table aliases are not allowed. Use full table names."
            )

        # ----------------------------------
        # Block JOIN table AS alias
        # ----------------------------------
        join_as_alias = (
            r"\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+AS\s+([a-zA-Z_][a-zA-Z0-9_]*)"
        )

        if re.search(
            join_as_alias,
            query,
            flags=re.IGNORECASE
        ):

            logger.warning(
                "Table alias detected using AS after JOIN."
            )

            return False, (
                "Table aliases are not allowed. Use full table names."
            )

        # ----------------------------------
        # Block FROM table alias
        # But avoid false positives like:
        # FROM gpos_sales WHERE
        # FROM gpos_sales JOIN
        # FROM gpos_sales GROUP
        # ----------------------------------
        from_alias = (
            r"\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+"
            r"(?!WHERE\b|JOIN\b|LEFT\b|RIGHT\b|INNER\b|OUTER\b|FULL\b|ON\b|GROUP\b|ORDER\b|LIMIT\b|HAVING\b|UNION\b|;)"
            r"([a-zA-Z_][a-zA-Z0-9_]*)"
        )

        if re.search(
            from_alias,
            query,
            flags=re.IGNORECASE
        ):

            logger.warning(
                "Table alias detected after FROM."
            )

            return False, (
                "Table aliases are not allowed. Use full table names."
            )

        # ----------------------------------
        # Block JOIN table alias
        # ----------------------------------
        join_alias = (
            r"\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+"
            r"(?!ON\b|USING\b|WHERE\b|JOIN\b|LEFT\b|RIGHT\b|INNER\b|OUTER\b|FULL\b|GROUP\b|ORDER\b|LIMIT\b|HAVING\b|;)"
            r"([a-zA-Z_][a-zA-Z0-9_]*)"
        )

        if re.search(
            join_alias,
            query,
            flags=re.IGNORECASE
        ):

            logger.warning(
                "Table alias detected after JOIN."
            )

            return False, (
                "Table aliases are not allowed. Use full table names."
            )

        return True, "No table aliases detected."

    except Exception as e:

        logger.error(
            f"Alias validation failed: {e}"
        )

        return False, str(e)


# ==========================================
# CHECK RETAILER FILTER
# ==========================================
def check_retailer_filter(
    sql_query: str
):

    """
    Ensures customer-specific tables are filtered by retailer_id.

    Required pattern example:
    WHERE gpos_sales.retailer_id = 10
    AND gpos_sales.retailer_id = 10
    """

    try:

        lowered_query = sql_query.lower()

        used_retailer_tables = []

        for table in RETAILER_FILTER_TABLES:

            if table.lower() in lowered_query:

                used_retailer_tables.append(
                    table
                )

        # If no retailer-specific business table is used,
        # do not force retailer_id.
        # Example:
        # SELECT retailer_id FROM gpos_retailer WHERE store_code = ...
        if not used_retailer_tables:

            return True, (
                "No retailer-specific table found."
            )

        # retailer_id must appear in query
        if "retailer_id" not in lowered_query:

            logger.warning(
                "Retailer-specific table used without retailer_id filter."
            )

            return False, (
                "Retailer filter missing. Query must filter by retailer_id."
            )

        # Check each used table has table_name.retailer_id condition
        for table in used_retailer_tables:

            pattern = (
                rf"\b{table}\.retailer_id\s*=\s*[0-9]+"
            )

            if not re.search(
                pattern,
                lowered_query,
                flags=re.IGNORECASE
            ):

                logger.warning(
                    f"Missing retailer_id filter for table: {table}"
                )

                return False, (
                    f"Missing retailer_id filter for {table}."
                )

        return True, (
            "Retailer filter validation successful."
        )

    except Exception as e:

        logger.error(
            f"Retailer filter validation failed: {e}"
        )

        return False, str(e)


# ==========================================
# NORMALIZE SPACES
# ==========================================
def normalize_spaces(
    value: str
):

    return re.sub(
        r"\s+",
        " ",
        value.strip()
    )
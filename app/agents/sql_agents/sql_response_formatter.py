from app.core.logging import get_logger


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# FORMAT SQL RESPONSE
# ==========================================
def format_sql_response(
    user_query: str,
    data: list,
    retailer_id: int | None = None
):

    try:

        logger.info(
            "Formatting SQL response for user."
        )

        if not data:

            return (
                "I could not find any matching records for your store."
            )

        query_lower = user_query.lower()

        # ==================================
        # SINGLE AGGREGATE RESULT
        # Example:
        # [{"average_tax": 191.88}]
        # [{"total_sales": 50000}]
        # [{"total_sales_records": 20}]
        # ==================================
        if (
            len(data) == 1
            and isinstance(data[0], dict)
        ):

            row = data[0]

            # ------------------------------
            # Average tax response
            # ------------------------------
            if (
                "average_tax" in row
                or "avg_tax" in row
                or "AVG(gpos_sales.tax)" in row
            ):

                value = (
                    row.get("average_tax")
                    or row.get("avg_tax")
                    or row.get("AVG(gpos_sales.tax)")
                )

                return (
                    f"The average tax paid for your store’s sales is ₹{value}."
                )

            # ------------------------------
            # Total sales response
            # ------------------------------
            if (
                "total_sales" in row
                or "revenue" in query_lower
                or "sales" in query_lower
            ):

                value = (
                    row.get("total_sales")
                    or first_value(row)
                )

                return (
                    f"The total sales for your store are ₹{value}."
                )

            # ------------------------------
            # Count response
            # ------------------------------
            if (
                "count" in query_lower
                or "how many" in query_lower
                or "total_sales_records" in row
            ):

                value = (
                    row.get("total_sales_records")
                    or first_value(row)
                )

                return (
                    f"There are {value} matching records for your store."
                )

            # ------------------------------
            # Generic single-row response
            # ------------------------------
            if len(row.keys()) == 1:

                key = list(row.keys())[0]

                value = row[key]

                readable_key = key.replace(
                    "_",
                    " "
                ).title()

                return (
                    f"{readable_key} for your store is {value}."
                )

            # ------------------------------
            # Multi-column single-row response
            # ------------------------------
            lines = []

            for key, value in row.items():

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

        # ==================================
        # MULTIPLE ROWS
        # ==================================
        preview_count = min(
            len(data),
            5
        )

        formatted_preview = []

        for index, row in enumerate(
            data[:preview_count],
            start=1
        ):

            row_lines = []

            for key, value in row.items():

                readable_key = key.replace(
                    "_",
                    " "
                ).title()

                row_lines.append(
                    f"{readable_key}: {value}"
                )

            formatted_preview.append(
                f"Result {index}:\n"
                + "\n".join(row_lines)
            )

        return (
            f"I found {len(data)} matching records for your store. "
            f"Here are the first {preview_count} results:\n\n"
            + "\n\n".join(formatted_preview)
        )

    except Exception as e:

        logger.error(
            f"SQL response formatting failed: {e}"
        )

        return (
            "I found the data, but could not format the response properly."
        )


# ==========================================
# GET FIRST VALUE FROM ROW
# ==========================================
def first_value(
    row: dict
):

    if not row:

        return None

    return list(row.values())[0]
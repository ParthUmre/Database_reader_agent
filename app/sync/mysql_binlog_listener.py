from pymysqlreplication import BinLogStreamReader

from pymysqlreplication.row_event import (
    WriteRowsEvent,
    UpdateRowsEvent,
    DeleteRowsEvent
)

from app.core.config import settings
from app.core.logging import get_logger

from app.sync.vector_sync_service import (
    sync_insert_event,
    sync_update_event,
    sync_delete_event
)


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# MONITORED TABLES
# ==========================================
MONITORED_TABLES = [
    "products",
    "warehouses",
    "finance_transactions"
]


# ==========================================
# START BINLOG LISTENER
# ==========================================
def start_binlog_listener():

    try:

        logger.info(
            "Starting MySQL binlog listener."
        )

        stream = BinLogStreamReader(

            connection_settings={

                "host": settings.MYSQL_HOST,

                "port": settings.MYSQL_PORT,

                "user": settings.MYSQL_USER,

                "passwd": settings.MYSQL_PASSWORD
            },

            server_id=1,

            blocking=True,

            only_tables=MONITORED_TABLES,

            only_events=[
                WriteRowsEvent,
                UpdateRowsEvent,
                DeleteRowsEvent
            ]
        )

        # ==================================
        # LISTEN FOR EVENTS
        # ==================================
        for event in stream:

            table_name = event.table

            # ==============================
            # INSERT EVENTS
            # ==============================
            if isinstance(
                event,
                WriteRowsEvent
            ):

                logger.info(
                    f"INSERT detected in "
                    f"{table_name}"
                )

                for row in event.rows:

                    row_data = row["values"]

                    sync_insert_event(
                        table_name=table_name,
                        row_data=row_data
                    )

            # ==============================
            # UPDATE EVENTS
            # ==============================
            elif isinstance(
                event,
                UpdateRowsEvent
            ):

                logger.info(
                    f"UPDATE detected in "
                    f"{table_name}"
                )

                for row in event.rows:

                    before_values = row[
                        "before_values"
                    ]

                    after_values = row[
                        "after_values"
                    ]

                    sync_update_event(
                        table_name=table_name,
                        before_values=before_values,
                        after_values=after_values
                    )

            # ==============================
            # DELETE EVENTS
            # ==============================
            elif isinstance(
                event,
                DeleteRowsEvent
            ):

                logger.info(
                    f"DELETE detected in "
                    f"{table_name}"
                )

                for row in event.rows:

                    row_data = row["values"]

                    sync_delete_event(
                        table_name=table_name,
                        row_data=row_data
                    )

    except Exception as e:

        logger.error(
            f"MySQL binlog listener failed: {e}"
        )

    finally:

        logger.info(
            "Closing MySQL binlog stream."
        )

        stream.close()
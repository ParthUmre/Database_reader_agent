from qdrant_client.models import (
    PointStruct
)
from uuid import uuid5, NAMESPACE_URL

from app.core.logging import get_logger

from app.vectorstore.qdrant_client import (
    qdrant_client,
    COLLECTION_NAME
)

from app.embeddings.embedding_service import (
    generate_embedding
)


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# VECTOR POINT ID
# ==========================================
def build_point_id(
    table_name: str,
    row_id
):

    return str(
        uuid5(
            NAMESPACE_URL,
            f"{table_name}:{row_id}"
        )
    )


# ==========================================
# BUILD SEARCHABLE TEXT
# ==========================================
def build_searchable_text(
    table_name: str,
    row_data: dict
):

    try:

        values = []

        for key, value in row_data.items():

            values.append(
                f"{key}: {value}"
            )

        searchable_text = (
            f"Table: {table_name}\n"
            + "\n".join(values)
        )

        return searchable_text

    except Exception as e:

        logger.error(
            f"Failed building searchable text: {e}"
        )

        raise e


# ==========================================
# UPSERT VECTOR
# ==========================================
def upsert_vector(
    table_name: str,
    row_data: dict
):

    try:

        row_id = row_data.get("id")
        point_id = build_point_id(
            table_name,
            row_id
        )

        searchable_text = (
            build_searchable_text(
                table_name,
                row_data
            )
        )

        embedding = generate_embedding(
            searchable_text
        )

        point = PointStruct(

            id=point_id,

            vector=embedding,

            payload={

                "table": table_name,

                "text": searchable_text,

                "metadata": row_data
            }
        )

        qdrant_client.upsert(

            collection_name=COLLECTION_NAME,

            points=[point]
        )

        logger.info(
            f"Vector upserted for "
            f"{table_name}:{row_id}"
        )

    except Exception as e:

        logger.error(
            f"Vector upsert failed: {e}"
        )


# ==========================================
# DELETE VECTOR
# ==========================================
def delete_vector(
    table_name: str,
    row_id
):

    try:

        point_id = build_point_id(
            table_name,
            row_id
        )

        qdrant_client.delete(

            collection_name=COLLECTION_NAME,

            points_selector=[point_id]
        )

        logger.info(
            f"Vector deleted for "
            f"{table_name}:{row_id}"
        )

    except Exception as e:

        logger.error(
            f"Vector deletion failed: {e}"
        )


# ==========================================
# INSERT EVENT HANDLER
# ==========================================
def sync_insert_event(
    table_name: str,
    row_data: dict
):

    try:

        logger.info(
            f"Syncing INSERT event for "
            f"{table_name}"
        )

        upsert_vector(
            table_name,
            row_data
        )

    except Exception as e:

        logger.error(
            f"INSERT sync failed: {e}"
        )


# ==========================================
# UPDATE EVENT HANDLER
# ==========================================
def sync_update_event(
    table_name: str,
    before_values: dict,
    after_values: dict
):

    try:

        logger.info(
            f"Syncing UPDATE event for "
            f"{table_name}"
        )

        upsert_vector(
            table_name,
            after_values
        )

    except Exception as e:

        logger.error(
            f"UPDATE sync failed: {e}"
        )


# ==========================================
# DELETE EVENT HANDLER
# ==========================================
def sync_delete_event(
    table_name: str,
    row_data: dict
):

    try:

        logger.info(
            f"Syncing DELETE event for "
            f"{table_name}"
        )

        row_id = row_data.get("id")

        delete_vector(
            table_name,
            row_id
        )

    except Exception as e:

        logger.error(
            f"DELETE sync failed: {e}"
        )
        

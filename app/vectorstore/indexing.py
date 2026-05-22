from uuid import uuid4

from qdrant_client.models import PointStruct

from app.vectorstore.qdrant_client import (
    qdrant_client,
    COLLECTION_NAME
)

from app.embeddings.embedding_service import (
    generate_embedding
)

from app.core.logging import get_logger


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# INDEX SINGLE DOCUMENT
# ==========================================
def index_document(
    text: str,
    metadata: dict
):

    try:

        logger.info(
            "Generating embedding for indexing."
        )

        embedding = generate_embedding(text)

        point = PointStruct(
            id=str(uuid4()),
            vector=embedding,
            payload={
                "text": text,
                "metadata": metadata
            }
        )

        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[point]
        )

        logger.info(
            "Document indexed successfully."
        )

        return True

    except Exception as e:

        logger.error(
            f"Document indexing failed: {e}"
        )

        raise e


# ==========================================
# INDEX MULTIPLE DOCUMENTS
# ==========================================
def index_documents(
    documents: list[dict]
):

    try:

        logger.info(
            f"Indexing {len(documents)} documents."
        )

        points = []

        for document in documents:

            text = document["text"]

            metadata = document.get(
                "metadata",
                {}
            )

            embedding = generate_embedding(
                text
            )

            point = PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "text": text,
                    "metadata": metadata
                }
            )

            points.append(point)

        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )

        logger.info(
            "Batch indexing completed successfully."
        )

        return True

    except Exception as e:

        logger.error(
            f"Batch indexing failed: {e}"
        )

        raise e
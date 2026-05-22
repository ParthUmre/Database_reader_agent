from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams
)

from app.core.config import settings
from app.core.logging import get_logger

# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# QDRANT CLIENT
# ==========================================
qdrant_client = QdrantClient(
    host=settings.QDRANT_HOST,
    port=settings.QDRANT_PORT
)


# ==========================================
# COLLECTION NAME
# ==========================================
COLLECTION_NAME = "enterprise_knowledge_base"


# ==========================================
# CREATE COLLECTION
# ==========================================
def create_collection():
    try:
        collections = qdrant_client.get_collections()
        existing_collections = [
            collection.name
            for collection in collections.collections
        ]

        if COLLECTION_NAME in existing_collections:
            # Check the existing collection's dimension size
            collection_info = qdrant_client.get_collection(COLLECTION_NAME)
            current_dim = collection_info.config.params.vectors.size

            # If it's still using the old 384 size, wipe it so we can upgrade to Gemini's 3072 size
            if current_dim == 384:
                logger.warning(
                    f"Collection '{COLLECTION_NAME}' exists with old dimension size (384). "
                    f"Deleting and recreating for Gemini (3072)..."
                )
                qdrant_client.delete_collection(collection_name=COLLECTION_NAME)
            else:
                logger.info(
                    f"Collection '{COLLECTION_NAME}' already exists with correct dimension size ({current_dim})."
                )
                return

        # Create the collection with Gemini's native 3072 dimensions
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=3072,  # ✨ Upgraded from 384 to 3072 for gemini-embedding-2
                distance=Distance.COSINE
            )
        )

        logger.info(
            f"Collection '{COLLECTION_NAME}' created successfully with 3072 dimensions."
        )

    except Exception as e:
        logger.error(
            f"Failed to create collection: {e}"
        )
        raise e


# ==========================================
# TEST QDRANT CONNECTION
# ==========================================
def test_qdrant_connection():
    try:
        collections = qdrant_client.get_collections()
        logger.info(
            "Qdrant connection established successfully."
        )
        return collections
    except Exception as e:
        logger.error(
            f"Qdrant connection failed: {e}"
        )
        raise e
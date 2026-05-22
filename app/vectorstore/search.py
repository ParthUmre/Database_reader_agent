from app.vectorstore.qdrant_client import (
    qdrant_client,
    COLLECTION_NAME
)

from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchValue
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
# SEMANTIC SEARCH
# ==========================================
def semantic_search(
    query: str,
    limit: int = 5
):

    try:

        logger.info(
            f"Performing semantic search for: {query}"
        )

        query_embedding = generate_embedding(
            query
        )

        results = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,

            query=query_embedding,

            limit= limit
        ).points

        formatted_results = []

        for result in results:

            formatted_results.append({
                "score": result.score,
                "text": result.payload.get("text"),
                "metadata": result.payload.get(
                    "metadata",
                    {}
                )
            })

        logger.info(
            f"Retrieved {len(formatted_results)} results."
        )

        return formatted_results

    except Exception as e:

        logger.error(
            f"Semantic search failed: {e}"
        )

        raise e


# ==========================================
# FILTERED SEMANTIC SEARCH
# ==========================================
def filtered_semantic_search(
    query: str,
    metadata_key: str,
    metadata_value: str,
    limit: int = 5
):

    try:

        logger.info(
            f"Performing filtered semantic search "
            f"for: {query}"
        )

        query_embedding = generate_embedding(
            query
        )

        results = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=5,
            

            query_filter=Filter(
                must=[
                    FieldCondition(
                        key=f"metadata.{metadata_key}",
                        match=MatchValue(
                            value=metadata_value
                        )
                    )
                ]
            )
        )

        formatted_results = []

        for result in results:

            formatted_results.append({
                "score": result.score,
                "text": result.payload.get("text"),
                "metadata": result.payload.get(
                    "metadata",
                    {}
                )
            })

        logger.info(
            f"Retrieved "
            f"{len(formatted_results)} "
            f"filtered results."
        )

        return formatted_results

    except Exception as e:

        logger.error(
            f"Filtered semantic search failed: {e}"
        )

        raise e

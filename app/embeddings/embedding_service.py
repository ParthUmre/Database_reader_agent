from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import settings
from app.core.logging import get_logger

# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# LOAD EMBEDDING MODEL
# ==========================================
logger.info(
    f"Loading embedding model: "
    f"{settings.EMBEDDING_MODEL}"
)

embedding_model = GoogleGenerativeAIEmbeddings(
    model=settings.EMBEDDING_MODEL,
    google_api_key=settings.GEMINI_API_KEY  # Note: langchain uses 'google_api_key' internally for this class
)

logger.info("Embedding model loaded successfully.")


# ==========================================
# GENERATE SINGLE EMBEDDING
# ==========================================
def generate_embedding(text: str):
    """Generates an embedding for a single text query using Gemini."""
    try:
        return embedding_model.embed_query(text)
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise e


# ==========================================
# GENERATE BATCH EMBEDDINGS
# ==========================================
def generate_embeddings_batch(texts: list[str]):
    """Generates embeddings for a list of document strings using Gemini."""
    try:
        return embedding_model.embed_documents(texts)
    except Exception as e:
        logger.error(f"Batch embedding generation failed: {e}")
        raise e


# ==========================================
# BACKWARD COMPATIBILITY ALIASES
# ==========================================
# In case other files expect the old naming convention
get_embedding = generate_embedding
get_batch_embeddings = generate_embeddings_batch
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):

    # ==========================================
    # APPLICATION
    # ==========================================
    APP_NAME: str = "Enterprise AI RAG System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ==========================================
    # API
    # ==========================================
    API_V1_PREFIX: str = "/api/v1"

    # ==========================================
    # MYSQL DATABASE
    # ==========================================
    MYSQL_HOST: str = Field(..., env="MYSQL_HOST")
    MYSQL_PORT: int = Field(..., env="MYSQL_PORT")
    MYSQL_USER: str = Field(..., env="MYSQL_USER")
    MYSQL_PASSWORD: str = Field(..., env="MYSQL_PASSWORD")
    MYSQL_DATABASE: str = Field(..., env="MYSQL_DATABASE")

    # ==========================================
    # QDRANT VECTOR DATABASE
    # ==========================================
    QDRANT_HOST: str = Field(..., env="QDRANT_HOST")
    QDRANT_PORT: int = Field(..., env="QDRANT_PORT")

    # ==========================================
    # GEMINI API
    # ==========================================
    GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY")
    EMBEDDING_MODEL: str = "gemini-embedding-2"

    # ==========================================
    # JWT AUTHENTICATION
    # ==========================================
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ==========================================
    # REDIS CACHE
    # ==========================================
    REDIS_HOST: str = Field(..., env="REDIS_HOST")
    REDIS_PORT: int = Field(..., env="REDIS_PORT")

    # ==========================================
    # LANGCHAIN / LANGGRAPH
    # ==========================================
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_PROJECT: str = "enterprise-rag-system"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
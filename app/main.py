from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import get_logger

from app.database.mysql.connection import test_db_connection
from app.database.mysql.connection import Base, engine
from app.database.mysql import model
from app.api.routes.product import router as product_router
from app.vectorstore.qdrant_client import (
    test_qdrant_connection,
    create_collection
)
from app.api.routes.chat import router as chat_router

# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# FASTAPI INITIALIZATION
# ==========================================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)


# ==========================================
# CORS MIDDLEWARE
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product_router)
app.include_router(chat_router)

# ==========================================
# STARTUP EVENT
# ==========================================
@app.on_event("startup")
async def startup_event():

    logger.info("Starting Enterprise AI RAG System...")
    test_db_connection()
    Base.metadata.create_all(bind=engine)
    test_qdrant_connection()
    create_collection()
    logger.info("Application startup complete.")


# ==========================================
# SHUTDOWN EVENT
# ==========================================
@app.on_event("shutdown")
async def shutdown_event():

    logger.info("Shutting down application...")


# ==========================================
# HEALTH CHECK ROUTE
# ==========================================
@app.get("/")
async def root():

    return {
        "message": "Enterprise AI RAG System Running"
    }


@app.get("/health")
async def health_check():

    return {
        "status": "healthy"
    }

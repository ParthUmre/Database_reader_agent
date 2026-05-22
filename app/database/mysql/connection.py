from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings
from app.core.logging import get_logger


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# DATABASE URL
# ==========================================
DATABASE_URL = (
    f"mysql+pymysql://"
    f"{settings.MYSQL_USER}:"
    f"{settings.MYSQL_PASSWORD}@"
    f"{settings.MYSQL_HOST}:"
    f"{settings.MYSQL_PORT}/"
    f"{settings.MYSQL_DATABASE}"
)


# ==========================================
# SQLALCHEMY ENGINE
# ==========================================
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)


# ==========================================
# SESSION FACTORY
# ==========================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==========================================
# BASE MODEL
# ==========================================
Base = declarative_base()


# ==========================================
# DATABASE SESSION DEPENDENCY
# ==========================================
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==========================================
# TEST CONNECTION
# ==========================================
def test_db_connection():

    try:
        with engine.connect() as connection:
            logger.info("MySQL database connected successfully.")

    except Exception as e:
        logger.error(f"MySQL connection failed: {e}")
        raise e
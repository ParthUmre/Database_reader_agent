from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials

from app.core.logging import get_logger

from app.security.jwt_handler import (
    verify_access_token
)


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# HTTP BEARER SCHEME
# ==========================================
security = HTTPBearer()


# ==========================================
# GET CURRENT USER
# ==========================================
def get_current_user(

    credentials: HTTPAuthorizationCredentials = (
        Depends(security)
    )
):

    try:

        token = credentials.credentials

        payload = verify_access_token(
            token
        )

        if payload is None:

            raise HTTPException(

                status_code=401,

                detail="Invalid or expired token."
            )

        logger.info(
            "User authenticated successfully."
        )

        return payload

    except Exception as e:

        logger.error(
            f"Authentication failed: {e}"
        )

        raise HTTPException(

            status_code=401,

            detail="Authentication failed."
        )
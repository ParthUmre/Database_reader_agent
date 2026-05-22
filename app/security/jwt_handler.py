from datetime import datetime
from datetime import timedelta

from jose import jwt
from jose import JWTError

from passlib.context import CryptContext

from app.core.config import settings
from app.core.logging import get_logger


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# PASSWORD HASHING
# ==========================================
pwd_context = CryptContext(

    schemes=["bcrypt"],

    deprecated="auto"
)


# ==========================================
# JWT CONFIG
# ==========================================
SECRET_KEY = settings.JWT_SECRET_KEY

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ==========================================
# HASH PASSWORD
# ==========================================
def hash_password(
    password: str
):

    return pwd_context.hash(
        password
    )


# ==========================================
# VERIFY PASSWORD
# ==========================================
def verify_password(
    plain_password: str,
    hashed_password: str
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# ==========================================
# CREATE ACCESS TOKEN
# ==========================================
def create_access_token(
    data: dict
):

    try:

        to_encode = data.copy()

        expire = (
            datetime.utcnow()
            + timedelta(
                minutes=(
                    ACCESS_TOKEN_EXPIRE_MINUTES
                )
            )
        )

        to_encode.update({

            "exp": expire
        })

        encoded_jwt = jwt.encode(

            to_encode,

            SECRET_KEY,

            algorithm=ALGORITHM
        )

        logger.info(
            "JWT token created successfully."
        )

        return encoded_jwt

    except Exception as e:

        logger.error(
            f"JWT creation failed: {e}"
        )

        raise e


# ==========================================
# VERIFY ACCESS TOKEN
# ==========================================
def verify_access_token(
    token: str
):

    try:

        payload = jwt.decode(

            token,

            SECRET_KEY,

            algorithms=[ALGORITHM]
        )

        logger.info(
            "JWT token verified successfully."
        )

        return payload

    except JWTError as e:

        logger.error(
            f"JWT verification failed: {e}"
        )

        return None
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.logging import get_logger


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# RESOLVE STORE CODE TO RETAILER ID
# ==========================================
def resolve_retailer_id_from_store_code(
    db: Session,
    store_code: str
):

    try:

        logger.info(
            f"Resolving retailer_id for store_code: {store_code}"
        )

        if not store_code:

            return {
                "success": False,
                "error": "Store code is required."
            }

        query = text("""
            SELECT
                gpos_retailer.retailer_id,
                gpos_retailer.store_code
            FROM gpos_retailer
            WHERE gpos_retailer.store_code = :store_code
            LIMIT 1;
        """)

        result = db.execute(
            query,
            {
                "store_code": store_code
            }
        ).fetchone()

        if not result:

            logger.warning(
                f"No retailer found for store_code: {store_code}"
            )

            return {
                "success": False,
                "error": "Invalid store code. No retailer found."
            }

        retailer_id = result.retailer_id

        logger.info(
            f"Resolved store_code {store_code} to retailer_id {retailer_id}"
        )

        return {
            "success": True,
            "store_code": result.store_code,
            "retailer_id": retailer_id
        }

    except Exception as e:

        logger.error(
            f"Failed to resolve retailer_id: {e}"
        )

        return {
            "success": False,
            "error": str(e)
        }


# ==========================================
# VALIDATE STORE CONTEXT
# ==========================================
def validate_store_context(
    db: Session,
    store_code: str
):

    result = resolve_retailer_id_from_store_code(
        db=db,
        store_code=store_code
    )

    if not result["success"]:

        return {
            "success": False,
            "error": result["error"]
        }

    return {
        "success": True,
        "store_code": result["store_code"],
        "retailer_id": result["retailer_id"]
    } 
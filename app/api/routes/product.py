from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.mysql.connection import get_db

from app.schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
    ProductResponse
)

from app.database.mysql.repositories.product_repository import (
    get_all_products,
    get_product_by_id,
    get_product_by_sku,
    create_product,
    update_product_quantity,
    delete_product
)

from app.core.logging import get_logger


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# ROUTER
# ==========================================
router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# ==========================================
# GET ALL PRODUCTS
# ==========================================
@router.get(
    "/",
    response_model=List[ProductResponse]
)
def fetch_products(
    db: Session = Depends(get_db)
):

    logger.info("GET /products called")

    return get_all_products(db)


# ==========================================
# GET PRODUCT BY ID
# ==========================================
@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
def fetch_product_by_id(
    product_id: int,
    db: Session = Depends(get_db)
):

    logger.info(
        f"GET /products/{product_id} called"
    )

    product = get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


# ==========================================
# CREATE PRODUCT
# ==========================================
@router.post(
    "/",
    response_model=ProductResponse
)
def create_new_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):

    logger.info("POST /products called")

    existing_product = get_product_by_sku(
        db,
        product.sku
    )

    if existing_product:
        raise HTTPException(
            status_code=400,
            detail="SKU already exists"
        )

    created_product = create_product(
        db,
        product.dict()
    )

    return created_product


# ==========================================
# UPDATE PRODUCT QUANTITY
# ==========================================
@router.put(
    "/{product_id}/quantity",
    response_model=ProductResponse
)
def update_quantity(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db)
):

    logger.info(
        f"Updating quantity for product ID: {product_id}"
    )

    updated_product = update_product_quantity(
        db,
        product_id,
        quantity
    )

    if not updated_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return updated_product


# ==========================================
# DELETE PRODUCT
# ==========================================
@router.delete("/{product_id}")
def remove_product(
    product_id: int,
    db: Session = Depends(get_db)
):

    logger.info(
        f"DELETE /products/{product_id} called"
    )

    deleted = delete_product(
        db,
        product_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return {
        "message": "Product deleted successfully"
    }
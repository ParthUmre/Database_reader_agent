from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.mysql.model import Product
from app.core.logging import get_logger


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# GET ALL PRODUCTS
# ==========================================
def get_all_products(db: Session):

    logger.info("Fetching all products.")

    return db.query(Product).all()


# ==========================================
# GET PRODUCT BY ID
# ==========================================
def get_product_by_id(
    db: Session,
    product_id: int
):

    logger.info(f"Fetching product with ID: {product_id}")

    return (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )


# ==========================================
# GET PRODUCT BY SKU
# ==========================================
def get_product_by_sku(
    db: Session,
    sku: str
):

    logger.info(f"Fetching product with SKU: {sku}")

    return (
        db.query(Product)
        .filter(Product.sku == sku)
        .first()
    )


# ==========================================
# CREATE PRODUCT
# ==========================================
def create_product(
    db: Session,
    product_data: dict
):

    logger.info("Creating new product.")

    product = Product(**product_data)

    db.add(product)

    db.commit()

    db.refresh(product)

    return product


# ==========================================
# UPDATE PRODUCT QUANTITY
# ==========================================
def update_product_quantity(
    db: Session,
    product_id: int,
    quantity: int
):

    logger.info(
        f"Updating quantity for product ID: {product_id}"
    )

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        return None

    product.quantity = quantity

    db.commit()

    db.refresh(product)

    return product


# ==========================================
# DELETE PRODUCT
# ==========================================
def delete_product(
    db: Session,
    product_id: int
):

    logger.info(f"Deleting product ID: {product_id}")

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        return False

    db.delete(product)

    db.commit()

    return True


# ==========================================
# GET LOW STOCK PRODUCTS
# ==========================================
def get_low_stock_products(
    db: Session,
    threshold: int = 10
):

    logger.info(
        f"Fetching products below stock threshold: {threshold}"
    )

    return (
        db.query(Product)
        .filter(Product.quantity < threshold)
        .all()
    )


# ==========================================
# GET TOP EXPENSIVE PRODUCTS
# ==========================================
def get_top_expensive_products(
    db: Session,
    limit: int = 5
):

    logger.info(
        f"Fetching top {limit} expensive products."
    )

    return (
        db.query(Product)
        .order_by(desc(Product.price))
        .limit(limit)
        .all()
    )
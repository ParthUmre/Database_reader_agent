from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.mysql.connection import Base


# ==========================================
# WAREHOUSE TABLE
# ==========================================
class Warehouse(Base):

    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)

    warehouse_name = Column(String(255), nullable=False)

    location = Column(String(255), nullable=False)

    capacity = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    products = relationship("Product", back_populates="warehouse")


# ==========================================
# PRODUCT TABLE
# ==========================================
class Product(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    product_name = Column(String(255), nullable=False)

    category = Column(String(100), nullable=False)

    sku = Column(String(100), unique=True, nullable=False)

    quantity = Column(Integer, nullable=False)

    price = Column(Float, nullable=False)

    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    warehouse = relationship("Warehouse", back_populates="products")

    transactions = relationship(
        "FinanceTransaction",
        back_populates="product"
    )


# ==========================================
# FINANCE TRANSACTIONS TABLE
# ==========================================
class FinanceTransaction(Base):

    __tablename__ = "finance_transactions"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(Integer, ForeignKey("products.id"))

    transaction_type = Column(String(50), nullable=False)
    # Example:
    # purchase
    # sale
    # refund

    amount = Column(Float, nullable=False)

    description = Column(Text)

    transaction_date = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    product = relationship(
        "Product",
        back_populates="transactions"
    )
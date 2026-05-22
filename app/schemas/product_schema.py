from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ==========================================
# BASE PRODUCT SCHEMA
# ==========================================
class ProductBase(BaseModel):

    product_name: str = Field(
        ...,
        min_length=2,
        max_length=255
    )

    category: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    sku: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    quantity: int = Field(
        ...,
        ge=0
    )

    price: float = Field(
        ...,
        gt=0
    )

    warehouse_id: int


# ==========================================
# CREATE PRODUCT SCHEMA
# ==========================================
class ProductCreate(ProductBase):
    pass


# ==========================================
# UPDATE PRODUCT SCHEMA
# ==========================================
class ProductUpdate(BaseModel):

    product_name: Optional[str] = None

    category: Optional[str] = None

    quantity: Optional[int] = Field(
        default=None,
        ge=0
    )

    price: Optional[float] = Field(
        default=None,
        gt=0
    )


# ==========================================
# RESPONSE PRODUCT SCHEMA
# ==========================================
class ProductResponse(ProductBase):

    id: int

    created_at: datetime

    class Config:
        from_attributes = True
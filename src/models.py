from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ProductModel(BaseModel):
    product_id: str = Field(..., min_length=3)
    name: str = Field(..., min_length=2)
    description: str = Field(..., min_length=10)
    price: float = Field(..., gt=0)
    category: str = Field(..., min_length=3)
    stock_status: str = Field(..., min_length=3)


class OrderModel(BaseModel):
    order_id: Optional[int] = None
    product_name: str = Field(min_length=2)
    quantity: int = Field(gt=0)
    customer_name: str = Field(min_length=2)
    price: float = Field(gt=0)
    total_price: float
    timestamp: datetime = Field(default_factory=datetime.now)

    @field_validator("total_price")
    def validate_total(cls, v, values):
        return values.data["price"] * values.data["quantity"]

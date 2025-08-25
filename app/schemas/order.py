from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.models.order import OrderStatus
from app.schemas.order_item import OrderItem, OrderItemCreate


class OrderBase(BaseModel):
    user_id: int
    shipping_address: str | None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    shipping_address: Optional[str] = None


class Order(OrderBase):
    id: int
    user_id: int
    status: OrderStatus
    total_amount: float
    # shipping_address: str | None
    created_at: datetime
    updated_at: datetime
    delivered_at: Optional[datetime] = None
    # items: List[OrderItem]

    class Config:
        from_attributes = True


class OrderWithItems(Order):
    items: List[OrderItem] = []

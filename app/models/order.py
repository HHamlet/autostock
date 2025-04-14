from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Integer, ForeignKey, String, Float, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderModel(BaseModel):
    __tablename__ = "orders"
    __table_args__ = (CheckConstraint('delivered_at IS NULL OR delivered_at >= created_at',
                                      name='check_delivery_date'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(String(20), nullable=False, default=OrderStatus.PENDING)

    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    shipping_address: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow,
                                                 onupdate=datetime.utcnow, nullable=False)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="orders", lazy="joined")
    items: Mapped[List["OrderItemModel"]] = relationship("OrderItemModel", back_populates="orders", lazy="joined",
                                                         cascade="all, delete-orphan")

    def __repr__(self):
        return f"OrderModel(OrderID: {self.id}, status: {self.status.value})"

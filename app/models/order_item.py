from sqlalchemy import Integer, ForeignKey, Float, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.order import OrderModel
from app.models.part import PartModel


class OrderItemModel(BaseModel):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint('quantity >= 0', name='check_quantity_positive'),
        CheckConstraint('unit_price >= 0', name='check_price_positive'),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey('orders.id'), nullable=False)
    part_id: Mapped[int] = mapped_column(Integer, ForeignKey('parts.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)

    order: Mapped["OrderModel"] = relationship("OrderModel", back_populates="items", lazy="joined")
    part: Mapped["PartModel"] = relationship("PartModel", back_populates="order_items", lazy="joined")

    def __repr__(self):
        return f"OrderItemModel {self.order_id} - {self.part.name if self.part else 'Unknown'} ({self.quantity})"

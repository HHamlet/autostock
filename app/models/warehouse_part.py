from sqlalchemy import ForeignKey, UniqueConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class WarehousePartModel(BaseModel):
    __tablename__ = "warehouse_part"
    __table_args__ = (UniqueConstraint("warehouse_id", "part_id", name="uix_warehouse_part"),)

    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), primary_key=True)
    part_id: Mapped[int] = mapped_column(ForeignKey("parts.id"), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    warehouse: Mapped["WarehouseModel"] = relationship(back_populates="warehouse_parts")
    part: Mapped["PartModel"] = relationship(back_populates="warehouse_parts")

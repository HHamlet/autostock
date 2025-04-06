from sqlalchemy import String, Table, ForeignKey, Column, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.car import CarModel
from app.models.category import CategoryModel
from app.models.manufacturer import ManufacturerModel
from app.models.base import BaseModel
from app.models.warehouse import WarehouseModel
from app.models.order import OrderModel


class PartModel(BaseModel):
    __tablename__ = "parts"
    __table_args__ = (
        CheckConstraint('price >= 0', name='check_price_positive'),
        CheckConstraint('qty_in_stock >= 0', name='check_stock_positive'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    part_number: Mapped[str] = mapped_column(String(50), nullable=False)
    manufacturer_part_number: Mapped[str]
    price: Mapped[float] = mapped_column(nullable=False)
    qty_in_stock: Mapped[int] = mapped_column(nullable=False, )
    description: Mapped[str] = mapped_column(Text, nullable=True)
    category_name: Mapped[int] = mapped_column(ForeignKey("categories.name"))

    category: Mapped["CategoryModel"] = relationship(back_populates="parts", lazy="joined")
    manufacturers: Mapped[list["ManufacturerModel"]] = relationship(secondary="part_manufacturer", back_populates="parts", lazy="joined")
    cars: Mapped[list["CarModel"]] = relationship(secondary="part_car", back_populates="parts", lazy="joined")
    warehouses: Mapped[list["WarehouseModel"]] = relationship(back_populates="parts", lazy="joined")

    order_items: Mapped[list["OrderItemModel"]] = relationship("OrderItemModel", back_populates="part", lazy="select")

    def __repr__(self):
        return (f"PartModel({self.name}, {self.part_number}, Category: {self.category}, "
                f"Manufacturer: {self.manufacturers})")


part_manufacturer = Table(
    "part_manufacturer", BaseModel.metadata,
    Column("part_id", ForeignKey("parts.id"), primary_key=True),
    Column("manufacturer_id", ForeignKey("manufacturers.id"), primary_key=True),
)

part_car = Table(
    "part_car", BaseModel.metadata,
    Column("part_id", ForeignKey("parts.id"), primary_key=True),
    Column("car_id", ForeignKey("cars.id"), primary_key=True),
)

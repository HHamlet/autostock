from sqlalchemy import ForeignKey, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel
from app.models.part import PartModel


class WarehouseModel(BaseModel):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str]
    location: Mapped[str]
    # part_id: Mapped[int] = mapped_column(ForeignKey("parts.id"))
    #
    # parts: Mapped[list["PartModel"]] = relationship(
    #     "PartModel", secondary="warehouse_part", back_populates="warehouses", lazy="joined")

    def __repr__(self):
        return f"WarehouseModel({self.name}, Location: {self.location})"


warehouse_part = Table(
    "warehouse_part",
    BaseModel.metadata,
    Column("warehouse_id", ForeignKey("warehouses.id"), primary_key=True),
    Column("part_id", ForeignKey("parts.id"), primary_key=True),
    Column("quantity", Integer, nullable=False, default=0),)

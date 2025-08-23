from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class WarehouseModel(BaseModel):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str]
    location: Mapped[str]

    warehouse_parts: Mapped[list["WarehousePartModel"]] = relationship("WarehousePartModel", back_populates="warehouse")

    def __repr__(self):
        return f"WarehouseModel({self.name}, Location: {self.location})"

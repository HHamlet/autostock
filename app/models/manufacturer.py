from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class ManufacturerModel(BaseModel):
    __tablename__ = "manufacturers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    website: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    parts: Mapped[list["PartModel"]] = relationship(
        secondary="part_manufacturer", back_populates="manufacturers", lazy="joined")

    def __repr__(self):
        return f"ManufacturerModel({self.name})"

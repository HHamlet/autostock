from typing import List, Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.part import PartModel
from app.models.base import BaseModel


class CategoryModel(BaseModel):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True)

    parent: Mapped[Optional["CategoryModel"]] = relationship(
        "CategoryModel", back_populates="subcategories", remote_side=[id])
    parts: Mapped[list["PartModel"]] = relationship(back_populates="category", lazy="joined")
    subcategories: Mapped[List["CategoryModel"]] = relationship(
        "CategoryModel", back_populates="parent", remote_side="CategoryModel.parent_id", lazy="select")

    def __repr__(self):
        return f"CategoryModel({self.id}, {self.name})"

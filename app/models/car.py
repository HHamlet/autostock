from enum import Enum
from typing import Optional
from sqlalchemy import String, Integer, Float, UniqueConstraint, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class EngineType(str, Enum):
    GASOLINE = "gasoline"
    DIESEL = "diesel"
    ELECTRIC = "electric"
    HYBRID = "hybrid"


class CarModel(BaseModel):
    __tablename__ = 'cars'
    __table_args__ = (
        UniqueConstraint('brand', 'model', 'year_start', 'engine_type', name='uix_car_definition'),
        Index('idx_cars_brand_model', 'brand', 'model'),
        CheckConstraint('year_end IS NULL OR year_end >= year_start', name='check_year_range'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    brand: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    year_start: Mapped[int] = mapped_column(Integer, nullable=False)
    year_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    engine_model: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    engine_type: Mapped[Optional[EngineType]] = mapped_column(String(50), nullable=True)
    engine_volume: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    body_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    parts: Mapped[list["PartModel"]] = relationship(secondary="part_car", back_populates="cars", lazy="joined")

    def __repr__(self):
        return f"CarModel({self.brand}, {self.model}, {self.year_start}-{self.year_end})"

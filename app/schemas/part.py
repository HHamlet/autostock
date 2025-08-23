from typing import List, Optional
from pydantic import BaseModel

from app.schemas.car import Car
from app.schemas.category import Category
from app.schemas.manufacturer import Manufacturer
from app.schemas.warehouse import WarehousePartRead


class PartBase(BaseModel):
    name: str
    part_number: str
    manufacturer_part_number: str
    price: float
    qty_in_stock: int
    description: Optional[str] = None
    image_url: Optional[str] = None
    category_name: Optional[str] = None


class PartCreate(PartBase):
    manufacturer_id: Optional[List[int]] = None
    car_id: Optional[List[int]] = None
    warehouse_id: int


class PartUpdate(BaseModel):
    name: Optional[str] = None
    part_number: Optional[str] = None
    manufacturer_part_number: Optional[str] = None
    price: Optional[float] = None
    qty_in_stock: Optional[int] = None
    category_name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    manufacturers_id: Optional[List[int]] = None
    cars_id: Optional[List[int]] = None
    warehouse_id: Optional[int] = None


class Part(PartBase):
    id: int

    class Config:
        from_attributes = True


class PartWithRelations(Part):
    category: Optional[Category] = None
    manufacturers: List[Manufacturer] = []
    cars: List[Car] = []
    warehouse_parts: List[WarehousePartRead] = []

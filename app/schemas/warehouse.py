from typing import Optional

from pydantic import BaseModel, field_validator


class WarehouseBase(BaseModel):
    name: str
    location: str


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None


class Warehouse(WarehouseBase):
    id: int

    class Config:
        from_attributes = True


class WarehousePartCreate(BaseModel):
    part_id: int
    quantity: int

    @field_validator('quantity')
    def quantity_must_be_non_negative(cls, v: int):
        if v < 0:
            raise ValueError('Quantity must be non-negative')
        return v

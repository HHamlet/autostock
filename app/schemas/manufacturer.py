from typing import Optional, List

from pydantic import BaseModel


class ManufacturerBase(BaseModel):
    name: str
    website: Optional[str] = None


class ManufacturerCreate(ManufacturerBase):
    pass


class ManufacturerUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None


class Manufacturer(ManufacturerBase):
    id: int
    # part: Optional[List["Part"]] | []

    class Config:
        orm_mode = True

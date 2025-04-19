from typing import Optional
from pydantic import BaseModel


class CarBase(BaseModel):
    brand: str
    model: str
    year_start: int
    year_end: Optional[int] = None
    engine_model: Optional[str] = None
    engine_type: Optional[str] = None
    engine_volume: Optional[str] = None
    body_type: Optional[str] = None


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    engine_model: Optional[str] = None
    engine_type: Optional[str] = None
    engine_volume: Optional[str] = None
    body_type: Optional[str] = None


class Car(CarBase):
    id: int

    class Config:
        orm_mode = True

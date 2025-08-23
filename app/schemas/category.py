from typing import Optional, List
from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None


class Category(CategoryBase):
    id: int
    # subcategories: List["Category"] = []

    class Config:
        from_attributes = True


class CategoryWithChildren(Category):
    subcategories: List["CategoryWithChildren"] = []


CategoryWithChildren.model_rebuild()

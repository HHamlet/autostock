from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db, get_current_active_admin
from app.models.user import UserModel
from app.schemas.category import Category, CategoryCreate, CategoryUpdate, CategoryWithChildren
from app.crud import categories

router = APIRouter()


@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(category_in: CategoryCreate, db: AsyncSession = Depends(get_async_db),
                          current_user: UserModel = Depends(get_current_active_admin),):

    return await categories.create_category(category_in=category_in, db=db, current_user=current_user)


@router.get("/tree", response_model=List[CategoryWithChildren])
async def read_category_tree(db: AsyncSession = Depends(get_async_db),):

    return await categories.get_category_tree(db=db)


@router.get("/{category_id}", response_model=CategoryWithChildren)
async def read_category(category_id: int, db: AsyncSession = Depends(get_async_db),):
    return await categories.get_category_by_id(category_id=category_id, db=db)


@router.put("/{category_id}", response_model=Category)
async def update_category(category_id: int, category_in: CategoryUpdate, db: AsyncSession = Depends(get_async_db),
                          current_user: UserModel = Depends(get_current_active_admin),):

    return await categories.update_category(category_id=category_id, category_in=category_in,
                                            db=db, current_user=current_user)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_async_db),
                          current_user: UserModel = Depends(get_current_active_admin),):
    return await categories.delete_category(category_id=category_id, db=db, current_user=current_user)

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.api.deps import get_async_db, get_current_active_admin
from app.models.category import CategoryModel
from app.models.user import UserModel
from app.schemas.category import Category, CategoryCreate, CategoryUpdate, CategoryWithChildren


async def get_categories_by_name(category_name: str, db: AsyncSession = Depends(get_async_db),):
    result = await db.execute(select(CategoryModel).options(selectinload(CategoryModel.subcategories)).
                              filter(CategoryModel.name == category_name))
    categories = result.scalars().first()
    return categories


async def get_category_by_id(category_id: int, db: AsyncSession = Depends(get_async_db), ):
    result = await db.execute(select(CategoryModel).options(selectinload(CategoryModel.subcategories)).
                              filter(CategoryModel.id == category_id))
    category = result.scalars().first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found", )
    return category


async def get_category_tree(db: AsyncSession = Depends(get_async_db), ):
    result = await db.execute(select(CategoryModel).
                              options(selectinload(CategoryModel.subcategories)).
                              filter(CategoryModel.parent_id.is_(None)))
    root_categories = result.scalars().all()
    return root_categories


async def create_category(category_in: CategoryCreate, db: AsyncSession = Depends(get_async_db),
                          current_user: UserModel = Depends(get_current_active_admin), ):
    result = await db.execute(select(CategoryModel).filter(CategoryModel.name == category_in.name))
    existing_category = result.scalars().first()

    if existing_category:
        raise HTTPException(status_code=400, detail="Category with this name already exists", )

    if category_in.parent_id:
        result = await db.execute(select(CategoryModel).filter(CategoryModel.id == category_in.parent_id))
        parent = result.scalars().first()

        if not parent:
            raise HTTPException(status_code=404, detail="Parent category not found", )

    category = CategoryModel(name=category_in.name, parent_id=category_in.parent_id, )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(category_id: int, category_in: CategoryUpdate, db: AsyncSession = Depends(get_async_db),
                          current_user: UserModel = Depends(get_current_active_admin), ):
    result = await db.execute(select(CategoryModel).filter(CategoryModel.id == category_id))
    category = result.scalars().first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found", )

    if category_in.name is not None and category_in.name != category.name:
        result = await db.execute(select(CategoryModel).
                                  filter(CategoryModel.name == category_in.name, CategoryModel.id != category_id))
        existing_category = result.scalars().first()

        if existing_category:
            raise HTTPException(status_code=400,
                                detail="Category with this name already exists", )
        category.name = category_in.name

    if category_in.parent_id is not None:
        if category_in.parent_id == category_id:
            raise HTTPException(status_code=400, detail="Category cannot be its own parent", )

        if category_in.parent_id:
            result = await db.execute(select(CategoryModel).filter(CategoryModel.id == category_in.parent_id))
            parent = result.scalars().first()

            if not parent:
                raise HTTPException(status_code=404, detail="Parent category not found", )

            current_parent_id = parent.id
            parent_chain = []

            while current_parent_id is not None:
                result = await db.execute(select(CategoryModel.id, CategoryModel.parent_id).
                                          filter(CategoryModel.id == current_parent_id))
                parent_data = result.first()
                if not parent_data:
                    break

                parent_chain.append(parent_data.id)
                current_parent_id = parent_data.parent_id

                if current_parent_id == category_id:
                    raise HTTPException(status_code=400,
                                        detail="Creating a cycle in category hierarchy is not allowed", )

        category.parent_id = category_in.parent_id

    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(category_id: int, db: AsyncSession = Depends(get_async_db),
                          current_user: UserModel = Depends(get_current_active_admin), ):
    result = await db.execute(select(CategoryModel).options(selectinload(CategoryModel.subcategories),
                                                            selectinload(CategoryModel.parts)).
                              filter(CategoryModel.id == category_id))
    category = result.scalars().first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found", )

    if category.subcategories:
        raise HTTPException(status_code=400,
                            detail="Cannot delete category with subcategories. Delete subcategories first.", )

    if category.parts:
        raise HTTPException(status_code=400,
                            detail="Cannot delete category with associated parts. Remove parts first.", )

    await db.delete(category)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

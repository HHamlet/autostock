from typing import Annotated
from fastapi import Depends, HTTPException, Response, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.api.deps import get_async_db, get_current_active_admin
from app.models import ManufacturerModel, UserModel
from app.schemas.manufacturer import ManufacturerCreate, ManufacturerUpdate
from app.schemas.pagination import Paginate, pagination_param, object_as_dict

paginate_dep = Annotated[Paginate, Depends(pagination_param)]


async def get_all_manufacturers(db: AsyncSession):
    result = await db.execute(select(ManufacturerModel))
    return result.unique().scalars().all()


async def get_manufacturers(paginate: paginate_dep, db: AsyncSession = Depends(get_async_db),):
    offset = (paginate.page - 1) * paginate.per_page
    total_result = await db.execute(select(func.count()).select_from(ManufacturerModel))
    total = total_result.scalar()
    result = await db.execute(select(ManufacturerModel).limit(paginate.per_page).offset(offset))
    manufacturers = result.unique().scalars().all()
    dict_manufacturers = [await object_as_dict(manufacturer) for manufacturer in manufacturers]

    return {"manufacturers": dict_manufacturers,
            "total": total,
            "page": paginate.page,
            "per_page": paginate.per_page}


async def get_manufacturer_by_name(name: str, db: AsyncSession = Depends(get_async_db),):

    result = await db.execute(select(ManufacturerModel).
                              options(selectinload(ManufacturerModel.parts)).
                              filter(ManufacturerModel.name == name))
    manufacturer = result.scalars().first()

    if not manufacturer:
        raise HTTPException(status_code=404, detail="Manufacturer not found",)
    return manufacturer


async def get_manufacturer_by_id(manufacturer_id: int, db: AsyncSession = Depends(get_async_db),):

    result = await db.execute(select(ManufacturerModel).
                              options(selectinload(ManufacturerModel.parts)).
                              filter(ManufacturerModel.id == manufacturer_id))
    manufacturer = result.scalars().first()

    if not manufacturer:
        raise HTTPException(status_code=404, detail="Manufacturer not found",)
    return manufacturer


async def create_manufacturer(manufacturer_in: ManufacturerCreate, db: AsyncSession = Depends(get_async_db),
                              current_user: UserModel = Depends(get_current_active_admin),):

    result = await db.execute(select(ManufacturerModel).filter(ManufacturerModel.name == manufacturer_in.name))
    existing_manufacturer = result.scalars().first()

    if existing_manufacturer:
        raise HTTPException(status_code=400,
                            detail="Manufacturer with this name already exists",)

    manufacturer = ManufacturerModel(name=manufacturer_in.name, website=manufacturer_in.website,)
    db.add(manufacturer)
    await db.commit()
    await db.refresh(manufacturer)
    return manufacturer


async def update_manufacturer(manufacturer_id: int, manufacturer_in: ManufacturerUpdate,
                              db: AsyncSession = Depends(get_async_db),
                              current_user: UserModel = Depends(get_current_active_admin),):

    result = await db.execute(select(ManufacturerModel).filter(ManufacturerModel.id == manufacturer_id))
    manufacturer = result.scalars().first()

    if not manufacturer:
        raise HTTPException(status_code=404, detail="Manufacturer not found",)

    if manufacturer_in.name is not None and manufacturer_in.name != manufacturer.name:
        result = await db.execute(select(ManufacturerModel).
                                  filter(ManufacturerModel.name == manufacturer_in.name,
                                         ManufacturerModel.id != manufacturer_id))
        existing_manufacturer = result.scalars().first()

        if existing_manufacturer:
            raise HTTPException(status_code=400,
                                detail="Manufacturer with this name already exists",)
        manufacturer.name = manufacturer_in.name

    if manufacturer_in.website is not None:
        manufacturer.website = manufacturer_in.website

    db.add(manufacturer)
    await db.commit()
    await db.refresh(manufacturer)
    return manufacturer


async def delete_manufacturer(manufacturer_id: int, db: AsyncSession = Depends(get_async_db),
                              current_user: UserModel = Depends(get_current_active_admin),):

    result = await db.execute(select(ManufacturerModel).
                              options(selectinload(ManufacturerModel.parts)).
                              filter(ManufacturerModel.id == manufacturer_id))
    manufacturer = result.scalars().first()

    if not manufacturer:
        raise HTTPException(status_code=404, detail="Manufacturer not found",)

    if manufacturer.parts:
        raise HTTPException(status_code=400,
                            detail="Cannot delete manufacturer with associated parts. Remove parts first.",)

    await db.delete(manufacturer)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from typing import Annotated
from fastapi import Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.api.deps import get_async_db, get_current_active_admin
from app.models import ManufacturerModel, UserModel
from app.schemas.manufacturer import ManufacturerCreate, ManufacturerUpdate
from app.schemas.pagination import Paginate, pagination_param, object_as_dict

paginate = Annotated[Paginate, Depends(pagination_param)]
offset = (paginate.page - 1) * paginate.per_page


async def read_manufacturers(db: AsyncSession = Depends(get_async_db),):

    result = await db.execute(select(ManufacturerModel).limit(int(paginate.per_page)).offset(offset))
    manufacturers = result.scalars().all()
    dict_manufacturer = [await object_as_dict(manufacturer) for manufacturer in manufacturers]

    return dict_manufacturer


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


async def read_manufacturer(manufacturer_id: int, db: AsyncSession = Depends(get_async_db),):

    result = await db.execute(select(ManufacturerModel).
                              options(selectinload(ManufacturerModel.parts)).
                              filter(ManufacturerModel.id == manufacturer_id))
    manufacturer = result.scalars().first()

    if not manufacturer:
        raise HTTPException(status_code=404, detail="Manufacturer not found",)
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

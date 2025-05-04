from typing import Annotated
from fastapi import Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.pagination import Paginate, pagination_param, object_as_dict
from app.api.deps import get_async_db, get_current_active_admin
from app.models.manufacturer import ManufacturerModel
from app.models.car import CarModel
from app.models import PartModel, UserModel
from app.schemas.part import PartCreate, PartUpdate

paginate_dep = Annotated[Paginate, Depends(pagination_param)]
# offset = (paginate.page - 1) * paginate.per_page


async def get_part_by_name(name: str, paginate: paginate_dep, db: AsyncSession = Depends(get_async_db), ):
    offset = (paginate.page - 1) * paginate.per_page
    result = await db.execute(select(PartModel).filter(PartModel.name.ilike(f"%{name}%")).
                              limit(int(paginate.per_page)).offset(offset))

    parts = result.unique().scalars().all()
    dict_part = [await object_as_dict(part) for part in parts]

    return dict_part


async def get_part_by_pn(part_n: str, paginate: paginate_dep, db: AsyncSession = Depends(get_async_db),):
    offset = (paginate.page - 1) * paginate.per_page
    result = await db.execute(select(PartModel).filter(PartModel.name == part_n).
                              limit(int(paginate.per_page)).offset(offset))

    parts = result.unique().scalars().all()
    dict_part = [await object_as_dict(part) for part in parts]

    return dict_part


async def get_part_by_m_pn(m_part_n: str, db: AsyncSession = Depends(get_async_db),):

    result = await db.execute(select(PartModel).filter(PartModel.name == m_part_n))

    parts = result.scalars().all()

    return parts


async def get_part_by_id(part_id: int, db: AsyncSession = Depends(get_async_db),):
    result = await db.execute(select(PartModel).options(
     selectinload(PartModel.manufacturers), selectinload(PartModel.cars), selectinload(PartModel.category),)
                              .filter(PartModel.id == part_id))
    part = result.scalars().all()

    if not part:
        raise HTTPException(status_code=404, detail="Part not found",)

    return part


async def get_parts():
    pass


async def create_part(part_in: PartCreate, db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_active_admin),):
    result = await db.execute(select(PartModel).
                              filter(PartModel.manufacturer_part_number == part_in.manufacturer_part_number))
    exist_part = result.scalars().first()
    if exist_part:
        raise HTTPException(status_code=400, detail="part is already exists")

    part = PartModel(name=part_in.name,
                     part_number=part_in.part_number,
                     manufacturer_part_number=part_in.manufacturer_part_number,
                     price=part_in.price,
                     qty_in_stock=part_in.qty_in_stock,
                     category_id=part_in.category_id,
                     description=part_in.description,)

    if part_in.manufacturer_ids:
        for manufacturer_id in part_in.manufacturer_ids:
            result = await db.execute(select(ManufacturerModel).filter(ManufacturerModel.id == manufacturer_id))
            manufacturer = result.scalars().first()
            if manufacturer:
                part.manufacturers.append(manufacturer)

    if part_in.car_ids:
        for car_id in part_in.car_ids:
            result = await db.execute(select(CarModel).filter(CarModel.id == car_id))
            car = result.scalars().first()
            if car:
                part.cars.append(car)

    db.add(part)
    await db.commit()
    await db.refresh(part)
    return part


async def update_part(part_id: int, part_in: PartUpdate, db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_active_admin), ):

    result = await db.execute(select(PartModel).options(
        selectinload(PartModel.manufacturers), selectinload(PartModel.cars)).filter(PartModel.id == part_id))
    part = result.scalars().first()

    if not part:
        raise HTTPException(status_code=404, detail="Part not found", )

    if part_in.name is not None:
        part.name = part_in.name
    if part_in.manufacturer_part_number is not None:
        result = await db.execute(select(PartModel).filter(
                PartModel.manufacturer_part_number == part_in.manufacturer_part_number, PartModel.id != part_id))
        existing_part = result.scalars().first()

        if existing_part:
            raise HTTPException(status_code=400, detail="A part with this Reference number already exists",)
        part.manufacturer_part_number = part_in.manufacturer_part_number
    if part_in.part_number is not None:
        part.part_number = part_in.part_number
    if part_in.price is not None:
        part.price = part_in.price
    if part_in.qty_in_stock is not None:
        part.qty_in_stock = part_in.qty_in_stock
    if part_in.category_id is not None:
        part.category_id = part_in.category_id
    if part_in.description is not None:
        part.description = part_in.description
    # if part_in.image_url is not None:
    #     part.image_url = part_in.image_url

    if part_in.manufacturer_ids is not None:
        from app.models.manufacturer import ManufacturerModel
        part.manufacturers = []
        for manufacturer_id in part_in.manufacturer_ids:
            result = await db.execute(select(ManufacturerModel).filter(ManufacturerModel.id == manufacturer_id))
            manufacturer = result.scalars().first()
            if manufacturer:
                part.manufacturers.append(manufacturer)

    if part_in.car_ids is not None:
        from app.models.car import CarModel
        part.cars = []
        for car_id in part_in.car_ids:
            result = await db.execute(select(CarModel).filter(CarModel.id == car_id))
            car = result.scalars().first()
            if car:
                part.cars.append(car)

    db.add(part)
    await db.commit()
    await db.refresh(part)
    return part


async def delete_part(part_id: int, db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_active_admin),):
    result = await db.execute(select(PartModel).filter(PartModel.id == part_id))
    part = result.scalars().first()

    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    await db.delete(part)
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def get_compatible_parts(car_id: int, paginate: paginate_dep, db: AsyncSession = Depends(get_async_db),):

    result = await db.execute(select(CarModel).filter(CarModel.id == car_id))
    car = result.scalars().first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found", )

    offset = (paginate.page - 1) * paginate.per_page
    result = await db.execute(select(PartModel).filter(PartModel.cars.any(id=car_id)).
                              limit(int(paginate.per_page)).offset(offset))
    parts = result.unique().scalars().all()
    dict_part = [await object_as_dict(part) for part in parts]
    return dict_part

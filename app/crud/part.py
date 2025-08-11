from typing import Annotated
from fastapi import Depends, HTTPException, Response, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.pagination import Paginate, pagination_param, object_as_dict
from app.api.deps import get_async_db, get_current_active_admin
from app.models.manufacturer import ManufacturerModel
from app.models.car import CarModel
from app.models import PartModel, UserModel, WarehousePartModel
from app.schemas.part import PartCreate, PartUpdate, PartWithRelations
from app.crud import categories, warehouses
from app.schemas.warehouse import WarehousePartCreate

paginate_dep = Annotated[Paginate, Depends(pagination_param)]


async def get_part_by_name(name: str, paginate: paginate_dep, db: AsyncSession = Depends(get_async_db), ):
    offset = (paginate.page - 1) * paginate.per_page
    result = await db.execute(select(PartModel).filter(PartModel.name.ilike(f"%{name}%")).
                              limit(int(paginate.per_page)).offset(offset))

    parts = result.unique().scalars().all()
    dict_part = [await object_as_dict(part) for part in parts]

    return dict_part


async def get_part_by_pn(part_pn: str, paginate: paginate_dep, db: AsyncSession = Depends(get_async_db), ):
    offset = (paginate.page - 1) * paginate.per_page
    result = await db.execute(select(PartModel).filter(PartModel.part_number == part_pn).
                              limit(int(paginate.per_page)).offset(offset))

    parts = result.unique().scalars().all()
    dict_part = [await object_as_dict(part) for part in parts]

    return dict_part


async def get_part_by_m_pn(m_part_n: str, db: AsyncSession = Depends(get_async_db), ):
    result = await db.execute(select(PartModel).filter(PartModel.manufacturer_part_number == m_part_n))

    parts = result.unique().scalars().all()

    return parts


async def get_part_by_category(category_id: int, db: AsyncSession = Depends(get_async_db),):
    result = await db.execute(select(PartModel).filter(PartModel.category_id == category_id))

    parts = result.unique().scalars().all()

    return parts


async def get_part_by_id(part_id: int, db: AsyncSession = Depends(get_async_db), ):
    result = await db.execute(select(PartModel).options(
        selectinload(PartModel.manufacturers),
        selectinload(PartModel.cars),
        selectinload(PartModel.category),
        selectinload(PartModel.warehouse_parts).selectinload(WarehousePartModel.warehouse)
        ).filter(PartModel.id == part_id))
    part = result.scalar_one_or_none()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found", )

    part_dict = PartWithRelations.model_validate(part)
    return part_dict


async def get_all_parts(paginate: paginate_dep, db: AsyncSession = Depends(get_async_db), ):
    offset = (paginate.page - 1) * paginate.per_page
    total_result = await db.execute(select(func.count()).select_from(PartModel))
    total = total_result.scalar()

    result = await db.execute(select(PartModel).limit(int(paginate.per_page)).offset(offset))

    parts = result.unique().scalars().all()
    dict_part = [await object_as_dict(part) for part in parts]

    return {"items": dict_part,
            "total": total,
            "page": paginate.page,
            "per_page": paginate.per_page}


async def create_part(part_in: PartCreate, db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_active_admin), ):
    result = await db.execute(select(PartModel).
                              filter(PartModel.manufacturer_part_number == part_in.manufacturer_part_number))
    exist_part = result.scalars().first()
    if exist_part:
        raise HTTPException(status_code=400, detail="part is already exists")
    category = await categories.get_categories_by_name(category_name=part_in.category_name, db=db)

    part = PartModel(name=part_in.name,
                     part_number=part_in.part_number,
                     manufacturer_part_number=part_in.manufacturer_part_number,
                     price=part_in.price,
                     qty_in_stock=0,
                     category_id=category,
                     description=part_in.description, )

    if part_in.manufacturer_id:
        for manufacturer_id in part_in.manufacturer_id:
            result = await db.execute(select(ManufacturerModel).filter(ManufacturerModel.id == manufacturer_id))
            manufacturer = result.scalars().first()
            if manufacturer:
                part.manufacturers.append(manufacturer)

    if part_in.car_id:
        for car_id in part_in.car_id:
            result = await db.execute(select(CarModel).filter(CarModel.id == car_id))
            car = result.scalars().first()
            if car:
                part.cars.append(car)

    db.add(part)
    await db.commit()
    await db.refresh(part)

    if part_in.warehouse_id:
        part_d = WarehousePartCreate(part_id=part.id, quantity=part_in.qty_in_stock)
        await warehouses.add_part_to_warehouse(warehouse_id=part_in.warehouse_id, part_data=part_d,
                                               db=db, current_user=current_user)
        await db.refresh(part)
    return part


async def update_part(part_id: int, part_in: PartUpdate, db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_active_admin), ):
    result = await db.execute(select(PartModel)
                              .options(selectinload(PartModel.manufacturers), selectinload(PartModel.cars))
                              .filter(PartModel.id == part_id))
    part = result.scalars().first()

    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    if part_in.manufacturer_part_number:
        result = await db.execute(select(PartModel).filter(
            PartModel.manufacturer_part_number == part_in.manufacturer_part_number,
            PartModel.id != part_id))

        if result.scalars().first():
            raise HTTPException(status_code=400, detail="A part with this Reference number already exists")

    if part_in.name is not None:
        part.name = part_in.name
    if part_in.manufacturer_part_number is not None:
        part.manufacturer_part_number = part_in.manufacturer_part_number
    if part_in.part_number is not None:
        part.part_number = part_in.part_number
    if part_in.price is not None:
        part.price = part_in.price
    if part_in.qty_in_stock is not None:
        part.qty_in_stock = part_in.qty_in_stock
    if part_in.description is not None:
        part.description = part_in.description
    # if part_in.image_url is not None:
    #     part.image_url = part_in.image_url
    if part_in.category_name is not None:
        part.category_id = await categories.get_categories_by_name(category_name=part_in.category_name, db=db)

    if part_in.manufacturers_id is not None:
        result = await db.execute(select(ManufacturerModel).filter(ManufacturerModel.id.in_(part_in.manufacturers_id)))
        part.manufacturers = result.unique().scalars().all()

    if part_in.cars_id is not None:
        result = await db.execute(select(CarModel).filter(CarModel.id.in_(part_in.cars_id)))
        part.cars = result.unique().scalars().all()

    # db.add(part)
    await db.commit()
    await db.refresh(part)
    return part


async def delete_part(part_id: int, db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_active_admin), ):
    result = await db.execute(select(PartModel).filter(PartModel.id == part_id))
    part = result.scalars().first()

    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    await db.delete(part)
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def get_compatible_parts(car_id: int, db: AsyncSession = Depends(get_async_db), ):
    result = await db.execute(select(CarModel).filter(CarModel.id == car_id))
    car = result.scalars().first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found", )

    # offset = (paginate.page - 1) * paginate.per_page
    result = await db.execute(select(PartModel).filter(PartModel.cars.any(id=car_id)))

    parts = result.unique().scalars().all()
    dict_part = [await object_as_dict(part) for part in parts]
    return dict_part

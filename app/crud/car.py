from typing import Annotated
from fastapi import Depends, HTTPException, Response, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db, get_current_active_admin
from app.models import CarModel, UserModel
from app.schemas.car import CarCreate, CarUpdate
from app.schemas.pagination import Paginate, pagination_param, object_as_dict

paginate_dep = Annotated[Paginate, Depends(pagination_param)]


async def get_cars(paginate: paginate_dep, db: AsyncSession = Depends(get_async_db),):
    offset = (paginate.page - 1) * paginate.per_page
    total_result = await db.execute(select(func.count()).select_from(CarModel))
    total = total_result.scalar()
    result = await db.execute(select(CarModel).limit(paginate.per_page).offset(offset))
    cars = result.unique().scalars().all()
    dict_car = [await object_as_dict(car) for car in cars]

    return {"cars": dict_car,
            "total": total,
            "page": paginate.page,
            "per_page": paginate.per_page}


async def get_all_cars(db: AsyncSession = Depends(get_async_db),):
    result = await db.execute(select(CarModel))
    return result.unique().scalars().all()


async def get_car_by_id(car_id: int, db: AsyncSession = Depends(get_async_db),):
    result = await db.execute(select(CarModel).where(CarModel.id == car_id))
    car = result.scalars().first()
    if not car:
        return None
    return await object_as_dict(car)


async def get_car_by_name(name: str, paginate: paginate_dep, db: AsyncSession = Depends(get_async_db),):
    offset = (paginate.page - 1) * paginate.per_page
    query = select(CarModel).filter((CarModel.brand + CarModel.model).ilike(f"%{name}%"))

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    result = await db.execute(query.limit(paginate.per_page).offset(offset))
    cars = result.unique().scalars().all()
    dict_cars = [await object_as_dict(car) for car in cars]

    return {
        "cars": dict_cars,
        "total": total,
        "page": paginate.page,
        "per_page": paginate.per_page
    }


async def create_car(car_in: CarCreate, db: AsyncSession = Depends(get_async_db),
                     current_user: UserModel = Depends(get_current_active_admin),):

    result = await db.execute(select(CarModel).filter(
            CarModel.brand == car_in.brand,
            CarModel.model == car_in.model,
            CarModel.year_start == car_in.year_start,
            CarModel.year_end == car_in.year_end,
            CarModel.engine_model == car_in.engine_model,
            CarModel.engine_type == car_in.engine_type,
            CarModel.engine_volume == car_in.engine_volume,
            CarModel.body_type == car_in.body_type
        )
    )
    existing_car = result.scalars().first()
    if existing_car:
        raise HTTPException(status_code=400, detail="This car already exists in the system")

    car = CarModel(
        brand=car_in.brand,
        model=car_in.model,
        year_start=car_in.year_start,
        year_end=car_in.year_end,
        engine_model=car_in.engine_model,
        engine_type=car_in.engine_type,
        engine_volume=car_in.engine_volume,
        body_type=car_in.body_type,
    )

    db.add(car)
    await db.commit()
    await db.refresh(car)
    return car


async def update_car(car_id: int, car_in: CarUpdate, db: AsyncSession = Depends(get_async_db),
                     current_user: UserModel = Depends(get_current_active_admin),):
    result = await db.execute(select(CarModel).where(CarModel.id == car_id))
    car_data = result.scalars().first()

    if car_data:
        car_data.brand = car_in.brand
        car_data.model = car_in.model
        car_data.year_start = car_in.year_start
        car_data.year_end = car_in.year_end
        car_data.engine_volume = car_in.engine_volume
        car_data.engine_model = car_in.engine_model
        car_data.engine_type = car_in.engine_type
        car_data.body_type = car_in.body_type
        await db.commit()
    await db.refresh(car_data)
    return car_data


async def delete_car(car_id: int, db: AsyncSession = Depends(get_async_db),
                     current_user: UserModel = Depends(get_current_active_admin),):
    result = await db.execute(select(CarModel).where(CarModel.id == car_id))
    car_data = result.scalars().first()
    if not car_data:
        raise HTTPException(status_code=404, detail="Car not found")

    await db.delete(car_data)
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

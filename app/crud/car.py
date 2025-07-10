from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db, get_current_active_admin
from app.models import CarModel, UserModel
from app.schemas.car import CarCreate


async def get_all_cars(db: AsyncSession):
    result = await db.execute(select(CarModel))
    return result.unique().scalars().all()


async def create_car(car_in: CarCreate, db: AsyncSession = Depends(get_async_db),
                     current_user: UserModel = Depends(get_current_active_admin),):

    result = await db.execute(select(CarModel).filter(
            CarModel.brand == car_in.brand,
            CarModel.model == car_in.model,
            CarModel.year_start == car_in.year_start,
            CarModel.engine_type == car_in.engine_type,
            CarModel.engine_model == car_in.engine_model
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

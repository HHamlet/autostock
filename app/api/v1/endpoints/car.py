from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter, status
from app.api.deps import get_async_db, get_current_active_admin
from app.models import UserModel
from app.schemas.car import CarCreate
from app.crud import car

router = APIRouter()


@router.post("/", response_model=CarCreate, status_code=status.HTTP_201_CREATED)
async def car_create(car_in: CarCreate, db: AsyncSession = Depends(get_async_db),
                     current_user: UserModel = Depends(get_current_active_admin),):

    return await car.create_car(car_in=car_in, db=db, current_user=current_user)

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db, get_current_active_admin
from app.models.user import UserModel
from app.schemas.manufacturer import Manufacturer, ManufacturerCreate, ManufacturerUpdate
from app.crud import manufacturer
from app.schemas.pagination import Paginate, pagination_param

router = APIRouter()


@router.get("/", response_model=List[Manufacturer])
async def manufacturers_read(paginate: Paginate = Depends(pagination_param), db: AsyncSession = Depends(get_async_db),):
    return await manufacturer.read_manufacturers(paginate=paginate, db=db)


@router.post("/", response_model=Manufacturer, status_code=status.HTTP_201_CREATED)
async def manufacturer_create(manufacturer_in: ManufacturerCreate, db: AsyncSession = Depends(get_async_db),
                              current_user: UserModel = Depends(get_current_active_admin),):

    return await manufacturer.create_manufacturer(manufacturer_in=manufacturer_in, db=db, current_user=current_user)


@router.get("/{manufacturer_id}", response_model=Manufacturer)
async def manufacturer_read(manufacturer_id: int, db: AsyncSession = Depends(get_async_db),):

    pass


@router.put("/{manufacturer_id}", response_model=Manufacturer)
async def manufacturer_update(manufacturer_id: int, manufacturer_in: ManufacturerUpdate,
                              db: AsyncSession = Depends(get_async_db),
                              current_user: UserModel = Depends(get_current_active_admin),):

    pass


@router.delete("/{manufacturer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def manufacturer_delete(manufacturer_id: int, db: AsyncSession = Depends(get_async_db),
                              current_user: UserModel = Depends(get_current_active_admin),):

    pass

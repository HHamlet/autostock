from typing import List, Optional
from fastapi import APIRouter, Depends, status, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db, get_current_active_admin
from app.models.user import UserModel
from app.schemas.part import Part, PartCreate, PartUpdate, PartWithRelations
from app.schemas.pagination import Paginate, pagination_param
from app.crud import part


router = APIRouter()
html_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_model=List[Part])
async def read_parts(paginate: Paginate = Depends(pagination_param), db: AsyncSession = Depends(get_async_db),
                     name: Optional[str] = None,
                     part_number: Optional[str] = None, manufacturer_part_number: Optional[str] = None):

    if name:
        parts = await part.get_part_by_name(paginate=paginate, name=name, db=db)
        return parts
    if part_number:
        parts = await part.get_part_by_pn(paginate=paginate, part_pn=part_number,  db=db)
        return parts
    if manufacturer_part_number:
        parts = await part.get_part_by_m_pn(m_part_n=manufacturer_part_number, db=db)
        return parts


@router.post("/", response_model=Part, status_code=status.HTTP_201_CREATED)
async def part_crate(part_in: PartCreate, db: AsyncSession = Depends(get_async_db),
                     current_user: UserModel = Depends(get_current_active_admin), ):
    return await part.create_part(part_in=part_in, db=db, current_user=current_user)


@router.get("/{part_id}", response_model=PartWithRelations)
async def read_part(part_id: int, db: AsyncSession = Depends(get_async_db), ):
    return await part.get_part_by_id(part_id=part_id, db=db)


@router.put("/{part_id}", response_model=Part)
async def part_update(part_id: int, part_in: PartUpdate, db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_active_admin), ):
    return await part.update_part(part_id=part_id, part_in=part_in, db=db, current_user=current_user)


@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def part_delete(part_id: int, db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_active_admin), ):
    return await part.delete_part(part_id=part_id, db=db, current_user=current_user)


@router.get("/compatible-with/{car_id}", response_model=List[Part])
async def get_compatible_parts(car_id: int, db: AsyncSession = Depends(get_async_db),):
    return await part.get_compatible_parts(car_id=car_id, db=db)

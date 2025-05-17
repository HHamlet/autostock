from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db, get_current_active_admin
from app.models.user import UserModel
from app.schemas.warehouse import Warehouse, WarehouseCreate, WarehouseUpdate, WarehousePartCreate
from app.crud import warehouses
from app.schemas.pagination import Paginate, pagination_param
router = APIRouter()


@router.get("/", response_model=List[Warehouse])
async def read_warehouses(paginate: Paginate = Depends(pagination_param), db: AsyncSession = Depends(get_async_db),):

    return await warehouses.get_warehouses(paginate=paginate, db=db)


@router.post("/", response_model=Warehouse, status_code=status.HTTP_201_CREATED)
async def warehouse_create(warehouse_in: WarehouseCreate, db: AsyncSession = Depends(get_async_db),
                           current_user: UserModel = Depends(get_current_active_admin),):

    return await warehouses.create_warehouse(warehouse_in=warehouse_in, db=db, current_user=current_user)


@router.get("/{warehouse_id}", response_model=Warehouse)
async def read_warehouse(warehouse_id: int, paginate: Paginate = Depends(pagination_param),
                         db: AsyncSession = Depends(get_async_db),):

    return await warehouses.get_warehouse(warehouse_id=warehouse_id, paginate=paginate, db=db)


@router.put("/{warehouse_id}", response_model=Warehouse)
async def update_warehouse(warehouse_id: int, warehouse_in: WarehouseUpdate,
                           db: AsyncSession = Depends(get_async_db),
                           current_user: UserModel = Depends(get_current_active_admin),):

    return await warehouses.update_warehouse(warehouse_id=warehouse_id, warehouse_in=warehouse_in,
                                             db=db, current_user=current_user)


@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_warehouse(warehouse_id: int, db: AsyncSession = Depends(get_async_db),
                           current_user: UserModel = Depends(get_current_active_admin), ):
    pass


@router.post("/{warehouse_id}/parts", status_code=status.HTTP_201_CREATED)
async def add_part_to_warehouse(warehouse_id: int, part_data: WarehousePartCreate,
                                db: AsyncSession = Depends(get_async_db),
                                current_user: UserModel = Depends(get_current_active_admin),):

    pass


@router.delete("/{warehouse_id}/parts/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_part_from_warehouse(warehouse_id: int, part_id: int, db: AsyncSession = Depends(get_async_db),
                                     current_user: UserModel = Depends(get_current_active_admin), ):
    pass

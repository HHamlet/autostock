from typing import List
from fastapi import APIRouter, Depends, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db, get_current_active_admin, get_current_user
from app.crud.car import get_all_cars
from app.crud.manufacturer import get_all_manufacturers
from app.crud.part import get_part_by_id
from app.crud.warehouses import get_all_warehouses
from app.models import WarehouseModel
from app.models.user import UserModel
from app.schemas.warehouse import Warehouse, WarehouseCreate, WarehouseUpdate, WarehousePartCreate
from app.crud import warehouses
from app.schemas.pagination import Paginate, pagination_param
router = APIRouter()
html_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


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

    return await warehouses.get_warehouse_parts(warehouse_id=warehouse_id, paginate=paginate, db=db)


@router.put("/{warehouse_id}", response_model=Warehouse)
async def update_warehouse(warehouse_id: int, warehouse_in: WarehouseUpdate,
                           db: AsyncSession = Depends(get_async_db),
                           current_user: UserModel = Depends(get_current_active_admin),):

    return await warehouses.update_warehouse(warehouse_id=warehouse_id, warehouse_in=warehouse_in,
                                             db=db, current_user=current_user)


@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_warehouse(warehouse_id: int, db: AsyncSession = Depends(get_async_db),
                           current_user: UserModel = Depends(get_current_active_admin), ):
    return await warehouses.delete_warehouse(warehouse_id=warehouse_id, db=db, current_user=current_user)


@router.post("/{warehouse_id}/parts", status_code=status.HTTP_201_CREATED)
async def add_part_to_warehouse(warehouse_id: int, part_data: WarehousePartCreate,
                                db: AsyncSession = Depends(get_async_db),
                                current_user: UserModel = Depends(get_current_active_admin),):
    return await warehouses.add_part_to_warehouse(warehouse_id=warehouse_id, part_data=part_data,
                                                  db=db, current_user=current_user)


@router.delete("/{warehouse_id}/parts/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_part_from_warehouse(warehouse_id: int, part_id: int, db: AsyncSession = Depends(get_async_db),
                                     current_user: UserModel = Depends(get_current_active_admin), ):
    pass


@html_router.get("/list", response_class=HTMLResponse)
async def warehouse_list(request: Request, paginate: Paginate = Depends(pagination_param),
                         db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_user),):
    items = await warehouses.get_warehouses(paginate, db)
    return templates.TemplateResponse("warehouses/list.html", {"request": request,
                                                               "current_user": current_user,
                                                               "warehouses": items,
                                                               "pagination": paginate, })


@html_router.get("/{warehouse_id}", response_class=HTMLResponse)
async def warehouse_detail(warehouse_id: int, request: Request, paginate: Paginate = Depends(pagination_param),
                           db: AsyncSession = Depends(get_async_db),
                           current_user: UserModel = Depends(get_current_active_admin)):

    parts = await warehouses.get_warehouse_parts(warehouse_id=warehouse_id, paginate=paginate, db=db)
    stmt = select(WarehouseModel).where(WarehouseModel.id == warehouse_id)
    result = await db.execute(stmt)
    warehouse = result.scalar_one_or_none()
    if not warehouse:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

    return templates.TemplateResponse("warehouses/detail.html", {"request": request,
                                                                 "current_user": current_user,
                                                                 "warehouse": warehouse,
                                                                 "parts": parts,
                                                                 "pagination": paginate, })


@html_router.get("/create", response_class=HTMLResponse)
async def warehouse_form(request: Request):
    return templates.TemplateResponse("warehouses/form.html", {
        "request": request,
        "form_action": "/warehouses/new",
        "form_title": "Create Warehouse"
    })


@html_router.post("/create")
async def warehouse_create(request: Request,
                           name: str = Form(...),
                           location: str = Form(...),
                           db: AsyncSession = Depends(get_async_db),
                           current_user=Depends(get_current_active_admin)):
    warehouse_in = WarehouseCreate(name=name, location=location)
    await warehouses.create_warehouse(warehouse_in, db=db, current_user=current_user)
    return RedirectResponse("/list", status_code=302)


@html_router.get("/add-part/{part_id}", response_class=HTMLResponse)
async def add_part_to_warehouse_form(part_id: int, request: Request,
                                     db: AsyncSession = Depends(get_async_db),
                                     current_user: UserModel = Depends(get_current_active_admin)):

    part = await get_part_by_id(part_id, db)
    manufacturers = await get_all_manufacturers(db)
    cars = await get_all_cars(db)

    warehouses_list = await get_all_warehouses(db)

    return templates.TemplateResponse("parts/form.html", {"request": request,
                                                          "part": part,
                                                          "part_id": part_id,
                                                          "manufacturers": manufacturers,
                                                          "cars": cars,
                                                          "add_to_warehouse": True,
                                                          "warehouses": warehouses_list,
                                                          "current_user": current_user})


@html_router.post("/add-part/{part_id}")
async def add_part_to_warehouse_post(request: Request, part_id: int,
                                     warehouse_id: int = Form(...),
                                     quantity: int = Form(...),
                                     db: AsyncSession = Depends(get_async_db),
                                     current_user: UserModel = Depends(get_current_active_admin)):
    part_data = WarehousePartCreate(part_id=part_id, quantity=quantity)
    await warehouses.add_part_to_warehouse(warehouse_id=warehouse_id, part_data=part_data,
                                           db=db, current_user=current_user)
    return RedirectResponse(url=f"/parts/{part_id}", status_code=302)

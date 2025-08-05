from typing import List, Optional
from fastapi import APIRouter, Depends, status, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db, get_current_active_admin, get_current_user
from app.models.user import UserModel
from app.schemas.part import Part, PartCreate, PartUpdate, PartWithRelations
from app.schemas.pagination import Paginate, pagination_param
from app.crud import part, manufacturer, car, warehouses


html_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@html_router.get("/", response_class=HTMLResponse)
async def list_parts_page(request: Request, paginate: Paginate = Depends(pagination_param),
                          db: AsyncSession = Depends(get_async_db),
                          current_user: UserModel = Depends(get_current_user),
                          name: Optional[str] = None, part_number: Optional[str] = None,
                          manufacturer_part_number: Optional[str] = None, ):
    parts = []
    if name:
        parts = await part.get_part_by_name(paginate=paginate, name=name, db=db)
        return templates.TemplateResponse("parts/list.html", {"request": request,
                                                              "parts": parts,
                                                              "current_user": current_user,})
    elif part_number:
        parts = await part.get_part_by_pn(paginate=paginate, part_pn=part_number, db=db)
        return templates.TemplateResponse("parts/list.html", {"request": request,
                                                              "parts": parts,
                                                              "current_user": current_user,})
    elif manufacturer_part_number:
        parts = await part.get_part_by_m_pn(m_part_n=manufacturer_part_number, db=db)
        return templates.TemplateResponse("parts/list.html", {"request": request,
                                                              "parts": parts,
                                                              "current_user": current_user,})
    else:
        result = await part.get_all_parts(paginate=paginate, db=db)

        return templates.TemplateResponse("parts/list.html", {"request": request,
                                                              "parts": result["items"],
                                                              "page": result["page"],
                                                              "limit": result["per_page"],
                                                              "total": result["total"],
                                                              "current_user": current_user, })


@html_router.get("/add_new", response_class=HTMLResponse)
async def part_create_page(request: Request, db: AsyncSession = Depends(get_async_db),
                           current_user: UserModel = Depends(get_current_active_admin)):

    manufacturers = await manufacturer.get_all_manufacturers(db=db)
    cars = await car.get_all_cars(db=db)
    warehouse = await warehouses.get_all_warehouses(db=db)

    return templates.TemplateResponse("parts/form.html", {"request": request,
                                                          "part": None,
                                                          "part_id": None,
                                                          "manufacturers": manufacturers,
                                                          "cars": cars,
                                                          "warehouses": warehouse,

                                                          "current_user": current_user})


@html_router.post("/add_new", response_model=Part, status_code=status.HTTP_201_CREATED)
async def html_part_crate(request: Request, db: AsyncSession = Depends(get_async_db),
                          current_user: UserModel = Depends(get_current_active_admin),
                          name: str = Form(...),
                          part_number: str = Form(...),
                          manufacturer_part_number: str = Form(...),
                          price: float = Form(...),
                          qty_in_stock: int = Form(...),
                          description: Optional[str] = Form(""),
                          image_url: Optional[str] = Form(...),
                          category_name: str = Form(""),
                          manufacturers_id: Optional[List[int]] = Form(...),
                          cars_id: Optional[List[int]] = Form(...),
                          warehouse_id: int = Form(...), ):

    part_in = PartCreate(name=name,
                         part_number=part_number,
                         manufacturer_part_number=manufacturer_part_number,
                         price=price,
                         qty_in_stock=qty_in_stock,
                         description=description,
                         image_url=image_url,
                         category_name=category_name,
                         manufacturer_id=manufacturers_id,
                         car_id=cars_id,
                         warehouse_id=warehouse_id,)

    await part.create_part(part_in=part_in, db=db, current_user=current_user)
    return RedirectResponse(url="/parts", status_code=302)


@html_router.get("/{part_id}/edit", response_class=HTMLResponse)
async def part_edit_page(request: Request, part_id: int,
                         db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_user)):
    part_data = await part.get_part_by_id(part_id, db=db)
    manufacturers = await manufacturer.get_all_manufacturers(db=db)
    cars = await car.get_all_cars(db=db)
    warehouse = await warehouses.get_all_warehouses(db=db)

    if not part_data:
        raise HTTPException(status_code=404, detail="Part not found")

    return templates.TemplateResponse("parts/form.html", {"request": request,
                                                          "part_id": part_id,
                                                          "part": part_data,
                                                          "manufacturers": manufacturers,
                                                          "cars": cars,
                                                          "warehouses": warehouses,

                                                          "current_user": current_user})


@html_router.post("/{part_id}/edit")
async def update_part_from_form(request: Request, part_id: int,
                                db: AsyncSession = Depends(get_async_db),
                                current_user: UserModel = Depends(get_current_active_admin),
                                name: Optional[str] = Form(...),
                                part_number: Optional[str] = Form(...),
                                manufacturer_part_number: Optional[str] = Form(...),
                                price: Optional[float] = Form(...),
                                category_name: Optional[str] = Form(""),
                                description: Optional[str] = Form(""),
                                image_url: Optional[str] = Form(...),
                                manufacturers_id: Optional[List[int]] = Form(...),
                                cars_id: Optional[List[int]] = Form(...),
                                warehouse_id: Optional[int] = Form(...),):

    part_in = PartUpdate(name=name,
                         part_number=part_number,
                         manufacturer_part_number=manufacturer_part_number,
                         price=price,
                         description=description,
                         image_url=image_url,
                         category_name=category_name,
                         manufacturers_id=manufacturers_id,
                         cars_id=cars_id,
                         warehouse_id=warehouse_id,)

    await part.update_part(part_id=part_id, part_in=part_in, db=db, current_user=current_user)
    return RedirectResponse(url=f"/parts/{part_id}", status_code=302)


@html_router.post("/{part_id}/delete")
async def delete_part_from_form(request: Request, part_id: int,
                                db: AsyncSession = Depends(get_async_db),
                                current_user: UserModel = Depends(get_current_active_admin)):

    await part.delete_part(part_id=part_id, db=db, current_user=current_user)
    return RedirectResponse(url="/parts", status_code=302)


@html_router.get("/{part_id}", response_class=HTMLResponse)
async def part_detail_page(request: Request, part_id: int,
                           db: AsyncSession = Depends(get_async_db),
                           current_user: UserModel = Depends(get_current_user)):
    part_model = await part.get_part_by_id(part_id=part_id, db=db)

    if not part_model:
        raise HTTPException(status_code=404, detail="Part not found")

    return templates.TemplateResponse("parts/detail.html", {"request": request,
                                                            "part": part_model,
                                                            "current_user": current_user, })



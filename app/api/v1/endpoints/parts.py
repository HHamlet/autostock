from typing import List, Optional
from fastapi import APIRouter, Depends, status, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db, get_current_active_admin, get_current_user
from app.models.user import UserModel
from app.schemas.part import Part, PartCreate, PartUpdate, PartWithRelations
from app.schemas.pagination import Paginate, pagination_param
from app.crud import part, manufacturer, car


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


@router.post("/", response_model=Part, status_code=status.HTTP_201_CREATED)
async def part_crate(part_in: PartCreate, db: AsyncSession = Depends(get_async_db),
                     current_user: UserModel = Depends(get_current_active_admin), ):
    return await part.create_part(part_in=part_in, db=db, current_user=current_user)


@html_router.get("/add_new", response_class=HTMLResponse)
async def part_create_page(request: Request, db: AsyncSession = Depends(get_async_db),
                           current_user: UserModel = Depends(get_current_user)):

    manufacturers = await manufacturer.get_all_manufacturers(db=db)
    cars = await car.get_all_cars(db=db)

    return templates.TemplateResponse("parts/form.html", {"request": request,
                                                          "part": None,
                                                          "part_id": None,
                                                          "manufacturers": manufacturers,
                                                          "cars": cars,
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
                          manufacturer_id: Optional[List[int]] = Form(...),
                          car_id: Optional[List[int]] = Form(...),
                          warehouse_id: int = Form(...), ):

    part_in = PartCreate(name=name,
                         part_number=part_number,
                         manufacturer_part_number=manufacturer_part_number,
                         price=price,
                         qty_in_stock=qty_in_stock,
                         description=description,
                         image_url=image_url,
                         category_name=category_name,
                         manufacturer_id=manufacturer_id,
                         car_id=car_id,
                         warehouse_id=warehouse_id,)

    await part.create_part(part_in=part_in, db=db, current_user=current_user)
    return RedirectResponse(url="/parts", status_code=302)


@router.get("/{part_id}", response_model=PartWithRelations)
async def read_part(part_id: int, db: AsyncSession = Depends(get_async_db), ):
    return await part.get_part_by_id(part_id=part_id, db=db)


@html_router.get("/{part_id}/edit", response_class=HTMLResponse)
async def part_edit_page(request: Request, part_id: int,
                         db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_user)):
    part_data = await part.get_part_by_id(part_id, db=db)
    manufacturers = await manufacturer.get_all_manufacturers(db=db)
    cars = await car.get_all_cars(db=db)
    if not part_data:
        raise HTTPException(status_code=404, detail="Part not found")

    return templates.TemplateResponse("parts/form.html", {"request": request,
                                                          "part_id": part_id,
                                                          "part": part_data,
                                                          "manufacturers": manufacturers,
                                                          "cars": cars,
                                                          "current_user": current_user})


@router.put("/{part_id}", response_model=Part)
async def part_update(part_id: int, part_in: PartUpdate, db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_active_admin), ):
    return await part.update_part(part_id=part_id, part_in=part_in, db=db, current_user=current_user)


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


@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def part_delete(part_id: int, db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_active_admin), ):
    return await part.delete_part(part_id=part_id, db=db, current_user=current_user)


@html_router.post("/{part_id}/delete")
async def delete_part_from_form(request: Request, part_id: int,
                                db: AsyncSession = Depends(get_async_db),
                                current_user: UserModel = Depends(get_current_active_admin)):

    await part.delete_part(part_id=part_id, db=db, current_user=current_user)
    return RedirectResponse(url="/parts", status_code=302)


@router.get("/compatible-with/{car_id}", response_model=List[Part])
async def get_compatible_parts(car_id: int, db: AsyncSession = Depends(get_async_db),):
    return await part.get_compatible_parts(car_id=car_id, db=db)


@html_router.get("/{part_id}", response_class=HTMLResponse)
async def part_detail_page(request: Request, part_id: int,
                           db: AsyncSession = Depends(get_async_db),
                           current_user: UserModel = Depends(get_current_user)):
    part_model = await part.get_part_by_id(part_id=part_id, db=db)

    if not part_model:
        raise HTTPException(status_code=404, detail="Part not found")
    # compatible_parts = await part.get_compatible_parts(car_id=part_id,  db=db)

    return templates.TemplateResponse("parts/detail.html", {"request": request,
                                                            "part": part_model,
                                                            "current_user": current_user, })

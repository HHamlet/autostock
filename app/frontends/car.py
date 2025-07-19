from typing import Optional
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db, get_current_active_admin, get_current_user
from app.crud import car
from app.models.user import UserModel
from app.schemas.car import CarCreate
from app.schemas.pagination import Paginate, pagination_param

html_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@html_router.get("/list", response_class=HTMLResponse)
async def get_car_list(request: Request, paginate: Paginate = Depends(pagination_param),
                       db: AsyncSession = Depends(get_async_db),
                       current_user: UserModel = Depends(get_current_user),
                       name: Optional[str] = None,):
    if name:
        items = await car.get_car_by_name(name=name, paginate=paginate, db=db)
    else:

        items = await car.get_cars(paginate, db)
    return templates.TemplateResponse("car/list.html", {"request": request,
                                                        "cars": items,
                                                        "page": items["page"],
                                                        "limit": items["per_page"],
                                                        "total": items["total"],
                                                        "current_user": current_user, })


@html_router.get("/add_new", response_class=HTMLResponse)
async def car_add_page(request: Request, db: AsyncSession = Depends(get_async_db),
                       current_user: UserModel = Depends(get_current_active_admin),):

    return templates.TemplateResponse("car/form.html", {"request": request,
                                                        "car": None,
                                                        "current_user": current_user})


@html_router.post("/add_new", response_class=HTMLResponse)
async def car_add_page(request: Request, db: AsyncSession = Depends(get_async_db),
                       current_user: UserModel = Depends(get_current_active_admin),
                       brand: str = Form(...),
                       model: str = Form(...),
                       year_start: int = Form(...),
                       year_end: Optional[int] = Form(...),
                       engine_model: Optional[str] = Form(...),
                       engine_type: Optional[str] = Form(...),
                       engine_volume: Optional[str] = Form(...),
                       body_type: Optional[str] = Form(...),):

    car_in = CarCreate(brand=brand,
                       model=model,
                       year_start=year_start,
                       year_end=year_end,
                       engine_model=engine_model,
                       engine_type=engine_type,
                       engine_volume=engine_volume,
                       body_type=body_type)

    await car.create_car(car_in=car_in, db=db, current_user=current_user)
    return RedirectResponse(url="car/list", status_code=302)


@html_router.get("/{car_id}", response_class=HTMLResponse)
async def car_detail_page(request: Request, car_id: int,
                          db: AsyncSession = Depends(get_async_db),
                          current_user: UserModel = Depends(get_current_user)):
    car_model = await car.get_car_by_id(car_id=car_id, db=db)
    if not car_model:
        raise HTTPException(status_code=404, detail="Car not found")

    return templates.TemplateResponse("car/detail.html", {"request": request,
                                                          "car": car_model,
                                                          "current_user": current_user, })

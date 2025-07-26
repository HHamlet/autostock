from PIL import Image
from PIL.Image import Resampling
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, Request, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db, get_current_active_admin, get_current_user
from app.crud import car
from app.models.user import UserModel
from app.schemas.car import CarCreate, CarUpdate
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
                       body_type: Optional[str] = Form(...),
                       image: Optional[UploadFile] = File(None)):

    car_in = CarCreate(brand=brand,
                       model=model,
                       year_start=year_start,
                       year_end=year_end,
                       engine_model=engine_model,
                       engine_type=engine_type,
                       engine_volume=engine_volume,
                       body_type=body_type)

    new_car = await car.create_car(car_in=car_in, db=db, current_user=current_user)

    target_width = 600
    target_height = 400

    if image and image.filename:
        ext = Path(image.filename).suffix.lower()
        if ext in [".jpeg", ".jpg", ".png"]:
            img_path = Path(f"static/cars/{new_car.id}.jpg")
            img_path.parent.mkdir(parents=True, exist_ok=True)

            with Image.open(image.file) as img:
                img = img.convert("RGB")
                img = img.resize((target_width, target_height), Resampling.LANCZOS)
                img.save(img_path, format="JPEG", quality=85)

    return RedirectResponse(url="/list", status_code=302)


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


@html_router.get("/{car_id}/edit", response_class=HTMLResponse)
async def car_edit_page(request: Request, car_id: int,
                        db: AsyncSession = Depends(get_async_db),
                        current_user: UserModel = Depends(get_current_active_admin)):
    car_data = await car.get_car_by_id(car_id=car_id, db=db)
    if not car_data:
        raise HTTPException(status_code=404, detail="Car not found")

    return templates.TemplateResponse("car/form.html", {"request": request,
                                                        "car_id": car_id,
                                                        "car": car_data,
                                                        "current_user": current_user})


@html_router.post("/{car_id}/edit")
async def update_part_from_form(request: Request, car_id: int,
                                db: AsyncSession = Depends(get_async_db),
                                current_user: UserModel = Depends(get_current_active_admin),
                                brand: Optional[str] = Form(...),
                                model: Optional[str] = Form(...),
                                year_start: Optional[int] = Form(...),
                                year_end: Optional[int] = Form(...),
                                engine_model: Optional[str] = Form(""),
                                engine_type: Optional[str] = Form(""),
                                engine_volume: Optional[str] = Form(...),
                                body_type: Optional[str] = Form(...),
                                image: Optional[UploadFile] = File(None)):

    car_in = CarUpdate(brand=brand,
                       model=model,
                       year_start=year_start,
                       year_end=year_end,
                       engine_model=engine_model,
                       engine_type=engine_type,
                       engine_volume=engine_volume,
                       body_type=body_type)

    await car.update_car(car_id=car_id, car_in=car_in, db=db, current_user=current_user)
    target_width = 600
    target_height = 400

    if image and image.filename:
        ext = Path(image.filename).suffix.lower()
        if ext in [".jpeg", ".jpg", ".png"]:
            img_path = Path(f"static/cars/{car_id}.jpg")
            img_path.parent.mkdir(parents=True, exist_ok=True)

            with Image.open(image.file) as img:
                img = img.convert("RGB")
                img = img.resize((target_width, target_height), Resampling.LANCZOS)
                img.save(img_path, format="JPEG", quality=85)

    return RedirectResponse(url=f"/cars/{car_id}", status_code=302)


@html_router.post("/{car_id}/delete")
async def delete_car_from_html(car_id: int, db: AsyncSession = Depends(get_async_db),
                               current_user: UserModel = Depends(get_current_active_admin)):
    await car.delete_car(car_id=car_id, db=db, current_user=current_user)
    return RedirectResponse(url="/cars/list?deleted=true", status_code=302)

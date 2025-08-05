from PIL import Image
from PIL.Image import Resampling
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, Request, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db, get_current_active_admin, get_current_user
from app.crud import manufacturer
from app.models.user import UserModel
from app.schemas.manufacturer import ManufacturerCreate, ManufacturerUpdate
from app.schemas.pagination import Paginate, pagination_param

html_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@html_router.get("/list", response_class=HTMLResponse)
async def get_manufacture_list(request: Request, paginate: Paginate = Depends(pagination_param),
                               db: AsyncSession = Depends(get_async_db),
                               current_user: UserModel = Depends(get_current_user),
                               name: Optional[str] = None, ):
    if name:
        items = await manufacturer.get_manufacturer_by_name(name=name, db=db)
    else:

        items = await manufacturer.get_manufacturers(paginate=paginate, db=db)
    return templates.TemplateResponse("manufacturers/list.html", {"request": request,
                                                                  "manufacturers": items,
                                                                  "page": items["page"],
                                                                  "limit": items["per_page"],
                                                                  "total": items["total"],
                                                                  "current_user": current_user, })


@html_router.get("/add_new", response_class=HTMLResponse)
async def manufacturer_add_page(request: Request, db: AsyncSession = Depends(get_async_db),
                                current_user: UserModel = Depends(get_current_active_admin),):

    return templates.TemplateResponse("manufacturers/form.html", {"request": request,
                                                                  "manufacturer": None,
                                                                  "current_user": current_user})


@html_router.post("/add_new", response_class=HTMLResponse)
async def manufacturer_add_page(request: Request, db: AsyncSession = Depends(get_async_db),
                                current_user: UserModel = Depends(get_current_active_admin),
                                name: str = Form(...),
                                website: str = Form(...),
                                image: Optional[UploadFile] = File(None)):

    manufacturer_in = ManufacturerCreate(name=name, website=website)

    new_manufacturer = await manufacturer.create_manufacturer(manufacturer_in=manufacturer_in, db=db,
                                                              current_user=current_user)

    target_width = 600
    target_height = 400

    if image and image.filename:
        ext = Path(image.filename).suffix.lower()
        if ext in [".jpeg", ".jpg", ".png"]:
            img_path = Path(f"static/manufacturers/{new_manufacturer.id}.jpg")
            img_path.parent.mkdir(parents=True, exist_ok=True)

            with Image.open(image.file) as img:
                img = img.convert("RGB")
                img = img.resize((target_width, target_height), Resampling.LANCZOS)
                img.save(img_path, format="JPEG", quality=85)

    return RedirectResponse(url="/manufactures/list", status_code=302)


@html_router.get("/{manufacturer_id}", response_class=HTMLResponse)
async def manufacturer_detail_page(request: Request, manufacturer_id: int,
                                   db: AsyncSession = Depends(get_async_db),
                                   current_user: UserModel = Depends(get_current_user)):
    manufacturer_model = await manufacturer.get_manufacturer_by_id(manufacturer_id=manufacturer_id, db=db)
    if not manufacturer_model:
        raise HTTPException(status_code=404, detail="Manufacturer not found")

    return templates.TemplateResponse("manufacturers/detail.html", {"request": request,
                                                                    "manufacturer": manufacturer_model,
                                                                    "current_user": current_user, })


@html_router.get("/{manufacturer_id}/edit", response_class=HTMLResponse)
async def manufacturer_edit_page(request: Request, manufacturer_id: int,
                                 db: AsyncSession = Depends(get_async_db),
                                 current_user: UserModel = Depends(get_current_active_admin)):
    manufacturer_data = await manufacturer.get_manufacturer_by_id(manufacturer_id=manufacturer_id, db=db)
    if not manufacturer_data:
        raise HTTPException(status_code=404, detail="Manufacturer not found")

    return templates.TemplateResponse("manufacturers/form.html", {"request": request,
                                                                  "manufacturer_id": manufacturer_id,
                                                                  "manufacturer": manufacturer_data,
                                                                  "current_user": current_user})


@html_router.post("/{manufacturer_id}/edit")
async def update_manufacturer_from_form(request: Request, manufacturer_id: int,
                                        db: AsyncSession = Depends(get_async_db),
                                        current_user: UserModel = Depends(get_current_active_admin),
                                        name: Optional[str] = Form(...),
                                        website: Optional[str] = Form(...),
                                        image: Optional[UploadFile] = File(None)):

    manufacturer_in = ManufacturerUpdate(name=name, website=website)

    await manufacturer.update_manufacturer(manufacturer_id=manufacturer_id, manufacturer_in=manufacturer_in,
                                           db=db, current_user=current_user)
    target_width = 600
    target_height = 400

    if image and image.filename:
        ext = Path(image.filename).suffix.lower()
        if ext in [".jpeg", ".jpg", ".png"]:
            img_path = Path(f"static/manufacturers/{manufacturer_id}.jpg")
            img_path.parent.mkdir(parents=True, exist_ok=True)

            with Image.open(image.file) as img:
                img = img.convert("RGB")
                img = img.resize((target_width, target_height), Resampling.LANCZOS)
                img.save(img_path, format="JPEG", quality=85)

    return RedirectResponse(url=f"/manufactures/{manufacturer_id}", status_code=302)


@html_router.post("/{manufacturer_id}/delete")
async def delete_manufacturer_from_html(manufacturer_id: int, db: AsyncSession = Depends(get_async_db),
                                        current_user: UserModel = Depends(get_current_active_admin)):
    await manufacturer.delete_manufacturer(manufacturer_id=manufacturer_id, db=db, current_user=current_user)
    return RedirectResponse(url="/manufacturers/list?deleted=true", status_code=302)

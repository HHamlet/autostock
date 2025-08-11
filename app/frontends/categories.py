from PIL import Image
from PIL.Image import Resampling
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, Request, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db, get_current_active_admin, get_current_user
from app.crud import categories
from app.schemas.category import CategoryCreate
from app.models.user import UserModel

html_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@html_router.get("/list", response_class=HTMLResponse)
async def get_all_category(request: Request, db: AsyncSession = Depends(get_async_db),
                           current_user: UserModel = Depends(get_current_user),):
    items = await categories.get_category_tree(db=db)
    return templates.TemplateResponse("categories/list.html", {"request": request,
                                                               "categories": items,
                                                               "current_user": current_user, })


@html_router.get("/add_new", response_class=HTMLResponse)
async def category_add_page(request: Request, db: AsyncSession = Depends(get_async_db),
                            current_user: UserModel = Depends(get_current_active_admin),):

    return templates.TemplateResponse("categories/form.html", {"request": request,
                                                               "category": None,
                                                               "current_user": current_user})


@html_router.post("/add_new", response_class=HTMLResponse)
async def category_add_page(request: Request, db: AsyncSession = Depends(get_async_db),
                            current_user: UserModel = Depends(get_current_active_admin),
                            name: str = Form(...),
                            image: Optional[UploadFile] = File(None),
                            parent_id: Optional[int] = None):

    categories_in = CategoryCreate(name=name, parent_id=parent_id)

    new_category = await categories.create_category(category_in=categories_in, db=db)

    target_width = 600
    target_height = 400

    if image and image.filename:
        ext = Path(image.filename).suffix.lower()
        if ext in [".jpeg", ".jpg", ".png"]:
            img_path = Path(f"static/categories/{new_category.id}.jpg")
            img_path.parent.mkdir(parents=True, exist_ok=True)

            with Image.open(image.file) as img:
                img = img.convert("RGB")
                img = img.resize((target_width, target_height), Resampling.LANCZOS)
                img.save(img_path, format="JPEG", quality=85)

    return RedirectResponse(url="/categories/list", status_code=302)

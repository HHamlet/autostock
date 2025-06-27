from typing import Optional
import uvicorn
from fastapi import FastAPI, Request, Depends, Cookie
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.api.deps import get_async_db
from app.api.v1.endpoints.user import router as user_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.car import router as car_router
from app.api.v1.endpoints.categories import router as cat_router
from app.api.v1.endpoints.manufacturers import router as man_router
from app.api.v1.endpoints.warehouses import router as ware_router
from app.api.v1.endpoints.warehouses import html_router as html_ware_router
from app.api.v1.endpoints.parts import router as part_router
from app.api.v1.endpoints.parts import html_router as part_html_router
from app.core.security import verify_access_token
from app.models import UserModel

app = FastAPI(title="Auto Parts Stock ...",
              description="An API for managing an auto parts and Stock/Warehouse ",
              version="0.1")

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(car_router,  prefix="/api/v1/cars", tags=["cars"])
app.include_router(cat_router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(man_router, prefix="/api/v1/manufacturers", tags=["manufacturer"])
app.include_router(ware_router, prefix="/api/v1/warehouses", tags=["warehouse"])
app.include_router(part_router, prefix="/api/v1/parts", tags=["parts"])

app.include_router(part_html_router, prefix="/parts", tags=["parts-html"])
app.include_router(html_ware_router, prefix="/warehouses", tags=["warehouse"])


@app.get("/")
async def home(request: Request, db: AsyncSession = Depends(get_async_db),
               access_token: Optional[str] = Cookie(default=None)):
    current_user = None
    if access_token:
        token = access_token.replace("Bearer ", "")
        try:
            token_data = verify_access_token(token)
            result = await db.execute(select(UserModel).filter(UserModel.id == int(token_data.sub)))
            user = result.scalars().first()
            if user and user.is_active:
                current_user = user
        except Exception:
            pass
    return templates.TemplateResponse("index.html", {"request": request, "current_user": current_user})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

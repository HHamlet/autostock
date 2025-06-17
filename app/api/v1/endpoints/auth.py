from fastapi import APIRouter, Depends, status, Request, Form, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db
from app.models import UserModel
from app.schemas.token import Token
from app.schemas.user import UserCreate
from app.crud import auth

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/login/api", response_model=Token)
async def login_access_token_api(db: AsyncSession = Depends(get_async_db),
                                 form_data: OAuth2PasswordRequestForm = Depends(),):
    return await auth.login_access_token(db=db, form_data=form_data)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")  # optional: if you're using token+cookie
    return response


@router.post("/login-form")
async def login_access_token_form(request: Request, db: AsyncSession = Depends(get_async_db),):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    form_data = OAuth2PasswordRequestForm(username=username, password=password)
    result = await db.execute(select(UserModel).filter(UserModel.username == form_data.username))
    user = result.scalars().first()
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

    token = await auth.login_access_token(db=db, form_data=form_data)
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=token['access_token'], httponly=True, secure=False)
    return response


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_async_db),):
    return await auth.register_user(user_in=user_in, db=db)


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.post("/register-form")
async def register_user_form(request: Request,
                             username: str = Form(...),
                             email: str = Form(...),
                             password: str = Form(...),
                             confirm_password: str = Form(...),
                             db: AsyncSession = Depends(get_async_db),):

    if password != confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    user_in = UserCreate(username=username, email=email, password=password)
    token = await auth.register_user(user_in=user_in, db=db)

    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {token['access_token']}", httponly=True)
    return response

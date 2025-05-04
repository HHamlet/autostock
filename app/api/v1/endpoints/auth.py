from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db
from app.schemas.token import Token
from app.schemas.user import UserCreate
from app.crud import auth

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_access_token(db: AsyncSession = Depends(get_async_db),
                             form_data: OAuth2PasswordRequestForm = Depends(),):
    return await auth.login_access_token(db=db, form_data=form_data)


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_async_db),):
    return await auth.register_user(user_in=user_in, db=db)

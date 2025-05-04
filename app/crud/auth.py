from datetime import timedelta
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import get_async_db
from app.core.config import settings
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models import UserModel
from app.schemas.user import UserCreate


async def login_access_token(db: AsyncSession = Depends(get_async_db),
                             form_data: OAuth2PasswordRequestForm = Depends(),):

    result = await db.execute(select(UserModel).filter(UserModel.username == form_data.username))
    user = result.scalars().first()
    if (not user) or (not verify_password(form_data.password, user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(subject=str(user.id), expires_delta=access_token_expires)

    return {"access_token": token, "token_type": "bearer", }


async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_async_db),):

    result = await db.execute(select(UserModel).filter(UserModel.email == user_in.email))
    user = result.scalars().first()
    if user:
        raise HTTPException(status_code=400, detail="The user with this email already exists in the system",)

    result = await db.execute(select(UserModel).filter(UserModel.username == user_in.username))
    user = result.scalars().first()
    if user:
        raise HTTPException(status_code=400, detail="The username is already taken",)

    user = UserModel(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        is_active=True,
        is_admin=user_in.is_admin,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(subject=str(user.id), expires_delta=access_token_expires)

    return {"access_token": token, "token_type": "bearer", }

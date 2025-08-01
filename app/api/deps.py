from datetime import datetime, timezone
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.security import verify_access_token
from app.core.session import async_session
from app.models.user import UserModel
from fastapi.security.utils import get_authorization_scheme_param

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_current_user(request: Request, db: AsyncSession = Depends(get_async_db),):

    auth_header = request.headers.get("Authorization")
    scheme, token = get_authorization_scheme_param(auth_header)
    if scheme.lower() != "bearer" or not token:
        token = request.cookies.get("access_token")
        print(f"access_token {token}")
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")

    token_data = verify_access_token(token)
    if token_data.exp < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result = await db.execute(select(UserModel).filter(UserModel.id == int(token_data.sub)))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return user


async def get_current_active_admin(
        current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

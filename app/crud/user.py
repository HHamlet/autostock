from datetime import timedelta
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db, get_current_active_admin
from app.core.config import settings
from app.core.security import get_password_hash, create_access_token
from app.models import UserModel
from app.schemas.user import UserCreate


async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_active_admin),):

    result = await db.execute(select(UserModel).filter(UserModel.email == user_in.email))

    user = result.scalars().first()
    if user:
        raise HTTPException(status_code=400, detail="The user with this email already exists in the system", )

    result = await db.execute(select(UserModel).filter(UserModel.username == user_in.username))
    user = result.scalars().first()
    if user:
        raise HTTPException(status_code=400, detail="The username is already taken", )

    user = UserModel(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        is_active=True,
        is_admin=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(subject=str(user.id), expires_delta=access_token_expires)

    return {"access_token": token, "token_type": "bearer", }

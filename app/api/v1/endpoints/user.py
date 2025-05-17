from fastapi import Depends, APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db, get_current_user, get_current_active_admin
from app.schemas.token import Token
from app.models import UserModel
from app.schemas.user import UserCreate, User
from app.crud import user

router = APIRouter()


@router.post("/create", response_model=Token, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_active_admin),):

    return await user.create_user(user_in=user_in, db=db, current_user=current_user)


@router.get("/me", response_model=User)
async def read_current_user(current_user: UserModel = Depends(get_current_user)):

    return current_user

from typing import Union, Optional, Any
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import jwt, JWTError
from pydantic import ValidationError
from hashlib import sha256


from app.core.config import settings
from app.schemas.token import TokenPayload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    salt_pass = f"{settings.SALT_KEY}:{password}"
    hash_generator = sha256(salt_pass.encode())
    return hash_generator.hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:

    hash_pass = get_password_hash(plain_password)

    return hash_pass == hashed_password


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

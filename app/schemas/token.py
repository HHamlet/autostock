from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    exp: Optional[datetime] = None
    sub: Optional[str] = None

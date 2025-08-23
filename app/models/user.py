from datetime import datetime
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class UserModel(BaseModel):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), info={"algorithm": "bcrypt"})
    registered_at: Mapped[datetime] = mapped_column(default=datetime.now)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    orders = relationship("OrderModel", back_populates="users", lazy="select")
    cart_items = relationship("OrderItemModel", back_populates="user", lazy="joined", cascade="all, delete-orphan")

    def __repr__(self):
        return f"UserModel({self.id}, UserName: {self.username}, active: {self.is_active}, admin : {self.is_admin})"

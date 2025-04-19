from pydantic import BaseModel


class OrderItemBase(BaseModel):
    part_id: int
    quantity: int


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    order_id: int
    unit_price: float

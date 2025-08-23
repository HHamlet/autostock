from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db, get_current_user
from app.models import UserModel, PartModel, OrderItemModel, OrderModel
from app.schemas.order_item import OrderItemCreate


async def add_to_cart(item: OrderItemCreate, db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_user), ):
    part = await db.scalar(select(PartModel).filter_by(id=item.part_id))
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    cart_item = await db.scalar(
        select(OrderItemModel).filter_by(user_id=current_user.id, part_id=item.part_id)
    )

    current_qty = cart_item.quantity if cart_item else 0
    if part.qty_in_stock < current_qty + item.quantity:
        raise HTTPException(status_code=400, detail=f"Not enough stock. Available: {part.qty_in_stock}",)

    if cart_item:
        cart_item.quantity += item.quantity
    else:
        cart_item = OrderItemModel(user_id=current_user.id,
                                   part_id=item.part_id,
                                   quantity=item.quantity,
                                   unit_price=part.price, )
        db.add(cart_item)

    await db.commit()
    await db.refresh(cart_item)

    return {"message": "Added to cart",
            "part_id": cart_item.part_id,
            "quantity": cart_item.quantity,
            "unit_price": cart_item.unit_price,
            "total_price": cart_item.unit_price * cart_item.quantity, }


async def view_cart(db: AsyncSession = Depends(get_async_db),
                    current_user: UserModel = Depends(get_current_user),):
    cart_items = (await db.execute(select(OrderItemModel).
                                   filter_by(user_id=current_user.id))).scalars().unique().all()

    if not cart_items:
        return {"cart": [], "total": 0}

    total = sum(item.quantity * item.unit_price for item in cart_items)

    return {
        "cart": [
            {
                "part_id": item.part_id,
                "part_name": item.part.name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.unit_price * item.quantity,
            }
            for item in cart_items
        ],
        "total": total,
    }


async def del_from_cart(part_id: int, db: AsyncSession = Depends(get_async_db),
                        current_user: UserModel = Depends(get_current_user),):
    cart_item = await db.scalar(
        select(OrderItemModel).filter_by(user_id=current_user.id, part_id=part_id))
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    await db.delete(cart_item)
    await db.commit()
    return {"message": f"Item {part_id} removed from cart"}


async def checkout_order(shipping_address: str, db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_user),):
    cart_items = (await db.execute(select(OrderItemModel).
                                   filter_by(user_id=current_user.id))).scalars().unique().all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order = OrderModel(user_id=current_user.id,
                       status="pending",
                       shipping_address=shipping_address,
                       total_amount=0.0,)
    db.add(order)
    await db.flush()

    total = 0.0
    for cart_item in cart_items:
        part = await db.get(PartModel, cart_item.part_id)

        if not part or part.qty_in_stock < cart_item.quantity:
            raise HTTPException(status_code=400,
                                detail=f"Not enough stock for {cart_item.part.name if part else 'Unknown'}")

        part.qty_in_stock -= cart_item.quantity

        order_item = OrderItemModel(order_id=order.id,
                                    part_id=cart_item.part_id,
                                    quantity=cart_item.quantity,
                                    unit_price=cart_item.unit_price,)
        db.add(order_item)
        total += cart_item.quantity * cart_item.unit_price

    order.total_amount = total

    for item in cart_items:
        await db.delete(item)

    await db.commit()
    await db.refresh(order)

    return {
        "message": "Order created",
        "order_id": order.id,
        "status": order.status,
        "total_amount": order.total_amount,
        "items": [
            {
                "part_id": i.part_id,
                "quantity": i.quantity,
                "unit_price": i.unit_price,
                "total_price": i.unit_price * i.quantity,
            }
            for i in order.items
        ],
    }


async def print_order(order_id: int, db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_user),):
    order = await db.get(OrderModel, order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"order_id": order.id,
            "status": order.status,
            "shipping_address": order.shipping_address,
            "created_at": order.created_at,
            "total_amount": order.total_amount,
            "items": [
                      {
                          "part_id": i.part_id,
                          "part_name": i.part.name,
                          "quantity": i.quantity,
                          "unit_price": i.unit_price,
                          "total_price": i.unit_price * i.quantity,
                      }
                      for i in order.items
                      ],
            }

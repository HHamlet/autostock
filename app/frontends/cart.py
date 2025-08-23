from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db, get_current_user
from app.models import UserModel
from app.schemas.order_item import OrderItemCreate
from app.crud import cart as cart_crud
from fastapi.templating import Jinja2Templates

html_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@html_router.get("/", response_class=HTMLResponse)
async def view_cart_page(request: Request, db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_user),):
    cart = await cart_crud.view_cart(db=db, current_user=current_user)
    return templates.TemplateResponse("cart/view.html", {"request": request,
                                                         "cart": cart,
                                                         "current_user": current_user})


@html_router.post("/add", response_class=HTMLResponse)
async def add_to_cart_page(request: Request,
                           part_id: int = Form(...),
                           quantity: int = Form(...),
                           db: AsyncSession = Depends(get_async_db),
                           current_user: UserModel = Depends(get_current_user),):
    item = OrderItemCreate(part_id=part_id, quantity=quantity)
    await cart_crud.add_to_cart(item=item, db=db, current_user=current_user)
    return RedirectResponse(url="/cart/", status_code=303)


@html_router.post("/delete/{part_id}", response_class=HTMLResponse)
async def delete_from_cart_page(part_id: int, db: AsyncSession = Depends(get_async_db),
                                current_user: UserModel = Depends(get_current_user),):
    await cart_crud.del_from_cart(part_id=part_id, db=db, current_user=current_user)
    return RedirectResponse(url="/cart/", status_code=303)


@html_router.post("/checkout", response_class=HTMLResponse)
async def checkout_page(request: Request,
                        shipping_address: str = Form(...),
                        db: AsyncSession = Depends(get_async_db),
                        current_user: UserModel = Depends(get_current_user),):
    order = await cart_crud.checkout_order(shipping_address=shipping_address, db=db, current_user=current_user)
    return RedirectResponse(url=f"/cart/order/{order['order_id']}", status_code=303)


@html_router.get("/order/{order_id}", response_class=HTMLResponse)
async def print_order_page(request: Request,
                           order_id: int,
                           db: AsyncSession = Depends(get_async_db),
                           current_user: UserModel = Depends(get_current_user),):
    order = await cart_crud.print_order(order_id=order_id, db=db, current_user=current_user)
    return templates.TemplateResponse("cart/order_detail.html", {"request": request,
                                                                 "order": order,
                                                                 "current_user": current_user})

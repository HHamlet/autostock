from typing import Annotated
from fastapi import Depends, HTTPException, Response, status
from sqlalchemy import select, update, insert, delete, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload, selectinload

from app.api.deps import get_async_db, get_current_active_admin
from app.models import WarehouseModel, UserModel, PartModel, WarehousePartModel
from app.schemas.pagination import Paginate, pagination_param, object_as_dict
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehousePartCreate

paginate_dep = Annotated[Paginate, Depends(pagination_param)]


async def get_warehouses(paginate: paginate_dep, db: AsyncSession = Depends(get_async_db),):
    offset = (paginate.page - 1) * paginate.per_page
    result = await db.execute(select(WarehouseModel).limit(paginate.per_page).offset(offset))
    warehouses = result.scalars().all()
    dict_ware = [await object_as_dict(part) for part in warehouses]
    return dict_ware


async def get_all_warehouses(db: AsyncSession):
    result = await db.execute(select(WarehouseModel))
    return result.scalars().all()


async def create_warehouse(warehouse_in: WarehouseCreate, db: AsyncSession = Depends(get_async_db),
                           current_user: UserModel = Depends(get_current_active_admin),):

    result = await db.execute(select(WarehouseModel).filter(
        WarehouseModel.name == warehouse_in.name, WarehouseModel.location == warehouse_in.location))
    existing_warehouse = result.scalars().first()

    if existing_warehouse:
        raise HTTPException(status_code=400,
                            detail="Warehouse with this name and location already exists", )

    warehouse = WarehouseModel(name=warehouse_in.name, location=warehouse_in.location, )
    db.add(warehouse)
    await db.commit()
    await db.refresh(warehouse)
    return warehouse


async def get_warehouse_parts(warehouse_id: int, paginate: paginate_dep, db: AsyncSession):
    offset = (paginate.page - 1) * paginate.per_page
    stmt = (select(WarehousePartModel).options(
        selectinload(WarehousePartModel.part)).where(WarehousePartModel.warehouse_id == warehouse_id)
            .limit(paginate.per_page).offset(offset))
    result = await db.execute(stmt)
    parts = result.scalars().all()

    dict_parts = []
    for wp in parts:
        part = wp.part
        if not part:
            continue
        dict_parts.append({"id": part.id,
                           "name": part.name,
                           "part_number": part.part_number,
                           "quantity": wp.quantity, })

    total_stmt = (select(func.count()).select_from(WarehousePartModel)
                  .filter(WarehousePartModel.warehouse_id == warehouse_id))
    total = await db.scalar(total_stmt)

    return {"items": dict_parts,
            "total": total,
            "page": paginate.page,
            "per_page": paginate.per_page, }


async def update_warehouse(warehouse_id: int, warehouse_in: WarehouseUpdate,
                           db: AsyncSession = Depends(get_async_db),
                           current_user: UserModel = Depends(get_current_active_admin),):

    result = await db.execute(select(WarehouseModel).filter(WarehouseModel.id == warehouse_id))
    warehouse = result.scalars().first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found", )

    if warehouse_in.name is not None:
        warehouse.name = warehouse_in.name

    if warehouse_in.location is not None:
        warehouse.location = warehouse_in.location

    db.add(warehouse)
    await db.commit()
    await db.refresh(warehouse)
    return warehouse


async def delete_warehouse(warehouse_id: int, db: AsyncSession = Depends(get_async_db),
                           current_user: UserModel = Depends(get_current_active_admin), ):
    result = await db.execute(select(WarehouseModel).filter(WarehouseModel.id == warehouse_id))
    warehouse = result.scalars().first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found", )

    result_wp = await db.execute(select(WarehousePartModel).filter(WarehousePartModel.warehouse_id == warehouse_id))
    warehouse_wp = result_wp.scalars().first()
    if warehouse_wp:
        raise HTTPException(status_code=400,
                            detail="Cannot delete warehouse with associated parts. Remove parts first.", )

    await db.delete(warehouse)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def add_part_to_warehouse(warehouse_id: int, part_data: WarehousePartCreate,
                                db: AsyncSession = Depends(get_async_db),
                                current_user: UserModel = Depends(get_current_active_admin),):

    try:
        warehouse = await db.get(WarehouseModel, warehouse_id)
        if not warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")

        part = await db.scalar(select(PartModel).options(noload(PartModel.category),
                                                         noload(PartModel.manufacturers),
                                                         noload(PartModel.cars))
                               .where(PartModel.id == part_data.part_id)
                               .with_for_update(nowait=True))
        if not part:
            raise HTTPException(status_code=404, detail="Part not found")

        existing_association = await db.scalar(select(WarehousePartModel).where(
                WarehousePartModel.warehouse_id == warehouse_id,
                WarehousePartModel.part_id == part_data.part_id))

        if existing_association:
            await db.execute(update(WarehousePartModel).
                             where(WarehousePartModel.warehouse_id == warehouse_id,
                                   WarehousePartModel.part_id == part_data.part_id,).
                             values(quantity=WarehousePartModel.quantity + part_data.quantity))
        else:
            await db.execute(insert(WarehousePartModel).values(warehouse_id=warehouse_id,
                                                               part_id=part_data.part_id,
                                                               quantity=part_data.quantity,))

        total_quantity = await recalculate_part_stock(part_id=part_data.part_id, db=db)
        await db.execute(update(PartModel).where(PartModel.id == part_data.part_id).values(qty_in_stock=total_quantity))

        await db.commit()

        return {
            "message": "Part quantity updated in warehouse" if existing_association
            else "Part added to warehouse successfully",
            "part_id": part_data.part_id,
            "warehouse_id": warehouse_id,
            "current_quantity": part_data.quantity,
            "total_in_stock": total_quantity
        }

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")


async def decrease_part_quantity_in_warehouse(warehouse_id: int, part_data: WarehousePartCreate,
                                              db: AsyncSession = Depends(get_async_db),
                                              current_user: UserModel = Depends(get_current_active_admin),):
    try:
        warehouse = await db.get(WarehouseModel, warehouse_id)
        if not warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")

        part = await db.scalar(
            select(PartModel).filter(PartModel.id == part_data.part_id).with_for_update()
        )
        if not part:
            raise HTTPException(status_code=404, detail="Part not found")

        existing_association = await db.scalar(select(WarehousePartModel).
                                               where(WarehousePartModel.warehouse_id == warehouse_id,
                                                     WarehousePartModel.part_id == part_data.part_id,))

        if not existing_association:
            raise HTTPException(status_code=404, detail="Part not found in warehouse")

        current_qty = existing_association.quantity
        if part_data.quantity > current_qty:
            raise HTTPException(status_code=400, detail="Cannot decrease below zero")

        await db.execute(update(WarehousePartModel).
                         where(WarehousePartModel.warehouse_id == warehouse_id,
                               WarehousePartModel.part_id == part_data.part_id,).
                         values(quantity=current_qty - part_data.quantity))

        total_quantity = await recalculate_part_stock(part_id=part_data.part_id, db=db)
        await db.execute(update(PartModel).where(PartModel.id == part_data.part_id).values(qty_in_stock=total_quantity))

        await db.commit()

        return {"message": f"Decreased part quantity by {part_data.quantity}",
                "remaining_in_warehouse": current_qty - part_data.quantity,
                "part_id": part_data.part_id,
                "warehouse_id": warehouse_id, }

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")


async def delete_part_from_warehouse(warehouse_id: int, part_id: int, db: AsyncSession = Depends(get_async_db),
                                     current_user: UserModel = Depends(get_current_active_admin),):
    try:
        warehouse = await db.get(WarehouseModel, warehouse_id)
        if not warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")

        part = await db.scalar(
            select(PartModel).filter(PartModel.id == part_id).with_for_update()
        )
        if not part:
            raise HTTPException(status_code=404, detail="Part not found")

        existing_association = await db.scalar(
            select(WarehousePartModel).where(WarehousePartModel.warehouse_id == warehouse_id,
                                             WarehousePartModel.part_id == part_id,))

        if not existing_association:
            raise HTTPException(status_code=404, detail="Part not found in warehouse")

        quantity_to_remove = existing_association.quantity

        await db.execute(
            delete(WarehousePartModel).where(WarehousePartModel.warehouse_id == warehouse_id,
                                             WarehousePartModel.part_id == part_id))

        total_quantity = await recalculate_part_stock(part_id=part_id, db=db)
        await db.execute(update(PartModel).where(PartModel.id == part_id).values(qty_in_stock=total_quantity))

        await db.commit()

        return {"message": "Part removed from warehouse",
                "removed_quantity": quantity_to_remove,
                "part_id": part_id,
                "warehouse_id": warehouse_id, }

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")


async def recalculate_part_stock(part_id: int, db: AsyncSession):
    total_quantity_stmt = (select(func.coalesce(func.sum(WarehousePartModel.quantity), 0)).
                           where(WarehousePartModel.part_id == part_id))

    total_quantity = await db.scalar(total_quantity_stmt)

    return total_quantity

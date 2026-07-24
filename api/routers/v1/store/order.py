from datetime import datetime, timezone
import uuid
import secrets
from typing import Literal, Optional, List
from fastapi import APIRouter, Depends, status, HTTPException, Header, Request
from schemas.store.entity import StoreSchema
from schemas.store.order import BaseVendorOrder, SingleVendorOrder
from models.user import Store
from libs.deps import get_store
from models.shopping import Order, OrderProduct, VendorOrder
from libs.limiter import limiter
from models.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

router = APIRouter(prefix="/{store_id}/v-orders")


@router.get("/")
async def get_vendor_orders(
    request: Request,
    store_id: str,
    q: Optional[Literal["paid", "unpaid"]] = None,
    store: StoreSchema = Depends(get_store),
    db: AsyncSession = Depends(get_db),
) -> Page[BaseVendorOrder]:
    stmt = (
        select(VendorOrder)
        .options(selectinload(VendorOrder.store))
        .where(func.lower(Store.slug) == store_id.lower().strip())
    )
    if q:
        stmt = (
            select(VendorOrder)
            .options(selectinload(VendorOrder.store))
            .where(
                func.lower(Store.slug) == store_id.lower().strip(),
                VendorOrder.status == q,
            )
        )

    result = await paginate(db, stmt)
    return result


@router.get("/{vid}")
@router.get("/order/{vid}")
async def get_vendor_order(
    request: Request,
    store_id: str,
    vid: uuid.UUID,
    store: StoreSchema = Depends(get_store),
    db: AsyncSession = Depends(get_db),
) -> SingleVendorOrder:

    stmt = (
        select(VendorOrder)
        .options(
            selectinload(VendorOrder.store),
            selectinload(VendorOrder.order).options(
                selectinload(Order.items).options(selectinload(OrderProduct.product))
            ),
        )
        .where(
            VendorOrder.vid == vid, func.lower(Store.slug) == store_id.lower().strip()
        )
    )

    v_order = await db.scalar(stmt)

    if not v_order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Order not found")

    order = v_order.order
    _order = BaseVendorOrder.model_validate(v_order).model_dump()

    order_items = order.items
    items = [
        {
            "product_name": item.product.name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
        }
        for item in order_items
    ]
    _order["items"] = items

    return _order

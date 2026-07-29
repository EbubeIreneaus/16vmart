from datetime import datetime, timezone
import uuid
import secrets
from typing import Literal, Optional, List
from fastapi import APIRouter, Depends, status, HTTPException, Header, Request
from models.user import Store
from libs.deps import get_admin
from schemas.user import UserShema
from schemas.store.entity import STORE_STATUS
from schemas.shopping import ORDER_STATUS, BaseOrderMini, SingleOrderOut
from schemas.admin.order import AdminSingleOrderOut, SingleVendorOrder, UpdateOrderSchema, MiniVendorOrder, VendorOrderUpdate
from schemas.checkout import CheckoutIn
from models.shopping import Order, OrderProduct, VendorOrder
from models.product import Product
from libs.limiter import limiter
from models.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from libs.redis import redis
from routers.v1.user import create_address, get_address
from sqlalchemy import func
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from settings import setting
from bg_task.config import get_arq_pool


router = APIRouter(prefix="/orders")


@router.patch("/status/{order_number}")
async def update_status(
    request: Request,
    order_number: str,
    body: UpdateOrderSchema,
    admin: UserShema = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    order = await db.scalar(
        select(Order).where(Order.order_number == order_number)
    )

    if not order:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="order dosen't exist")
    
    order.status = body.status
    return {"success": True}

@router.get("/")
async def get_orders(
    request: Request,
    s: Optional[ORDER_STATUS | Literal["all"]] = "all",
    admin: UserShema = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
) -> Page[BaseOrderMini]:
    stmt = select(Order)
    
    if s != "all":
        stmt = stmt.where(Order.status == s)

    stmt = stmt.order_by(Order.created_at.desc())
    result = await paginate(db, stmt)
    return result

@router.get("/vendor-orders")
async def get_vendor_orders(
    request: Request,
    q: Optional[Literal['paid', 'unpaid']] = None,
    admin: UserShema = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
)-> Page[MiniVendorOrder]:
    stmt = select(VendorOrder)
    if q:
        stmt = select(VendorOrder).where(VendorOrder.status == q)
    
    result = await paginate(db, stmt)
    return result

@router.get("/{order_number}")
async def get_order(
    request: Request,
    order_number: str,
    admi: UserShema = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
) -> AdminSingleOrderOut:
    
    order = await db.scalar(
        select(Order)
        .join(Order.delivery_address)
        .join(Order.items)
        .options(
            selectinload(Order.delivery_address),
            selectinload(Order.vendors).options(
                selectinload(VendorOrder.store)
            ),
            selectinload(Order.user),
            selectinload(Order.items).options(
                selectinload(OrderProduct.product).options(
                    selectinload(Product.images),
                    selectinload(Product.category),
                )
            ),
        )
        .where(Order.order_number == order_number)
    )

    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Order not found")

    return order

@router.get("/vendor-order/{vid}")
async def get_vendor_order(
    request: Request,
    vid: uuid.UUID,
    admin: UserShema = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
)-> SingleVendorOrder:

    stmt = select(VendorOrder).options(
        selectinload(VendorOrder.store),
        selectinload(VendorOrder.order)
    ).where(VendorOrder.vid == vid)
    
    result = await db.scalar(stmt)

    if not result:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    return result

@router.patch("/vendor-order-status/{vid}")
async def update_status(
    request: Request,
    vid: uuid.UUID,
    body: VendorOrderUpdate,
    admin: UserShema = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    order = await db.scalar(
        select(VendorOrder).where(VendorOrder.vid == vid)
    )

    if not order:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="order dosen't exist")
    
    order.status = body.status
    return {"success": True}
from schemas.store.entity import InternalStoreSchema
from datetime import timedelta
from datetime import timezone
from datetime import datetime
from models.user import Store
from sqlalchemy.orm import selectinload
from libs.deps import get_store
from models.shopping import VendorOrder
from sqlalchemy import func
from models.product import Product
from sqlalchemy import select
from models.db import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from math import degrees
from fastapi import APIRouter, Request
from libs.limiter import limiter
from libs.logger import logger
from .product import router as ProductRouter
from .entity import router as EntityRouter
from .cat import router as CategoryRouter
from .order import router as OrderRouter

router = APIRouter(prefix="/store")

router.include_router(ProductRouter)
router.include_router(EntityRouter)
router.include_router(CategoryRouter)
router.include_router(OrderRouter)


@router.get("/{store_id}/metadata")
@limiter.limit("60/minute", error_message="Too many requests, try again later")
async def get_store_metadata(
    request: Request,
    store_id: str,
    store: InternalStoreSchema = Depends(get_store),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)

    product_live_count = (
        await db.execute(
            select(func.count(Product.id)).where(
                Product.store_id == store.id,
                Product.deleted == False,
                Product.available == True,
            )
        )
    ).scalar_one()

    month_order_count = (
        await db.execute(
            select(func.count(VendorOrder.id)).where(
                VendorOrder.store_id == store.id,
                VendorOrder.created_at >=(now - timedelta(days=30)),
            )
        )
    ).scalar_one()

    pending_payout = (
        await db.execute(
            select(func.sum(VendorOrder.subtotal)).where(
                VendorOrder.store_id == store.id,
                VendorOrder.status == "unpaid",
            )
        )
    ).scalar_one()

    logger.info(f"Store {store.id} metadata retrieved. Pending payout: {pending_payout}")

    return {
        "live_products": product_live_count or 0,
        "monthly_orders": month_order_count or 0,
        "pending_payout": pending_payout or 0,
    }

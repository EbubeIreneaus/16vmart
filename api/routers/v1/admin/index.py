from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.db import get_db
from models.user import User, Store
from models.shopping import Order
from schemas.user import STATUS, UserShema
from schemas.store.entity import STORE_STATUS
from libs.deps import get_admin
from .product import router as ProductRouter, c_router as CategoryRouter
from .user import router as UserRouter
from .store import router as StoreRouter
from .order import router as OrderRouter

router = APIRouter(prefix="/admin")

router.include_router(ProductRouter)
router.include_router(CategoryRouter)
router.include_router(UserRouter)
router.include_router(StoreRouter)
router.include_router(OrderRouter)


@router.get("/metadata")
async def get_admin_metadata(
    admin: UserShema = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    users_count = (
        await db.execute(
            select(func.count(User.id)).where(User.status == STATUS.ACTIVE)
        )
    ).scalar_one()

    stores_count = (
        await db.execute(
            select(func.count(Store.id)).where(Store.status == STORE_STATUS.ACTIVE)
        )
    ).scalar_one()

    orders_count = (
        await db.execute(select(func.count(Order.id)))
    ).scalar_one()

    return {
        "users": users_count or 0,
        "stores": stores_count or 0,
        "orders": orders_count or 0,
    }



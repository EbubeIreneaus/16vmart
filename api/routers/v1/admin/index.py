from fastapi import APIRouter
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


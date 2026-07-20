from fastapi import APIRouter
from .product import router as ProductRouter
from .entity import router as EntityRouter
from .cat import router as CategoryRouter
from .order import router as OrderRouter

router = APIRouter(prefix="/store")

router.include_router(ProductRouter)
router.include_router(EntityRouter)
router.include_router(CategoryRouter)
router.include_router(OrderRouter)


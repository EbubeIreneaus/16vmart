from fastapi import APIRouter
from .product import router as ProductRouter
from .entity import router as EntityRouter

router = APIRouter(prefix="/store")

router.include_router(ProductRouter)
router.include_router(EntityRouter)


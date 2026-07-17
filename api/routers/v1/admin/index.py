from fastapi import APIRouter
from .product import router as ProductRouter, c_router as CategoryRouter

router = APIRouter(prefix="/admin")

router.include_router(ProductRouter)
router.include_router(CategoryRouter)


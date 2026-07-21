from fastapi import FastAPI, Depends
from routers.v1 import cat, product
from routers.v1 import auth
from routers.v1 import wishlist
from routers.v1 import order
from routers.v1 import cart
from routers.v1.store.index import router as StoreRouter
from routers.v1.admin.index import router as AdminRouter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
add_pagination(app)

app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(AdminRouter, prefix="/api/v1", tags=["Administrative"])
app.include_router(cat.router, prefix="/api/v1", tags=["Product"])  # category
app.include_router(StoreRouter, prefix="/api/v1", tags=["Store (Vendors)"])
app.include_router(product.router, prefix="/api/v1", tags=["Product"])
app.include_router(cart.router, prefix="/api/v1", tags=["Shopping"])
app.include_router(wishlist.router, prefix="/api/v1", tags=["Shopping"])
app.include_router(order.router, prefix="/api/v1", tags=["Shopping"])

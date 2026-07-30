from arq import Worker
from settings import setting
from fastapi import FastAPI, Depends
from routers.v1 import cat, product
from routers.v1 import auth
from routers.v1 import wishlist
from routers.v1 import order
from routers.v1 import cart
from routers.v1 import user
from routers.v1.store.index import router as StoreRouter
from routers.v1.admin.index import router as AdminRouter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware
from libs.limiter import limiter
from libs.logger import logger
from arq import run_worker
import asyncio
from bg_task.config import WorkerSettings

app = FastAPI()
app.state.limiter = limiter

worker_instance = None

@app.on_event("startup")
async def start_worker():
    global worker_instance
    worker_instance = Worker(
        functions=WorkerSettings.functions,
        redis_settings=WorkerSettings.redis_settings,
        poll_delay=WorkerSettings.pool_delay,
        queue_name=WorkerSettings.queue_name
    )
    asyncio.create_task(worker_instance.async_run())

@app.on_event("shutdown")
async def shutdown_worker():
    if worker_instance:
        await worker_instance.close()

logger.info("Initializing 16vmart FastAPI Application...")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"https://{setting.APP_URL}"],
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
app.include_router(user.router, prefix="/api/v1", tags=["User"])
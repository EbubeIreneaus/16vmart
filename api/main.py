from fastapi import FastAPI, Depends
from routers.v1 import auth, products
from routers.v1.store.index import router as StoreRouter
from routers.v1.admin.index import router as AdminRouter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
 

app = FastAPI()

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.include_router(auth.router, prefix="/api")
app.include_router(AdminRouter, prefix="/api")
app.include_router(products.c_router, prefix="/api") #category
app.include_router(StoreRouter, prefix="/api")


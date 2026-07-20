from arq import create_pool
from arq.connections import RedisSettings
from .auth import update_session, send_welcome_email
from .order import update_order, create_vendor_orders

REDIS_SETTING = RedisSettings()

async def get_arq_pool():
    arq_redis = await create_pool(REDIS_SETTING)
    return arq_redis


class WorkerSettings:
    functions = [update_session, send_welcome_email, update_order, create_vendor_orders]
    redis_settings = REDIS_SETTING
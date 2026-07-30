from settings import setting
from arq import create_pool
from arq.connections import RedisSettings
from .auth import update_session, send_welcome_email
from .order import update_order, create_vendor_orders

REDIS_SETTING = RedisSettings(
    host=setting.REDIS_HOST,
    port=setting.REDIS_PORT,
    password=setting.REDIS_PASS,
    username=setting.REDIS_USER,
    ssl=setting.REDIS_SSL,
)


async def get_arq_pool():
    arq_redis = await create_pool(REDIS_SETTING)
    return arq_redis


class WorkerSettings:
    functions = [update_session, send_welcome_email, update_order, create_vendor_orders]
    redis_settings = REDIS_SETTING
    queue_name = "16vmart"
    pool_delay = 3600

from arq import create_pool
from arq.connections import RedisSettings
from .auth import update_session, send_welcome_email

REDIS_SETTING = RedisSettings()

async def get_arq_pool():
    arq_redis = await create_pool(REDIS_SETTING)
    return arq_redis


class WorkerSettings:
    functions = [update_session, send_welcome_email]
    redis_settings = REDIS_SETTING
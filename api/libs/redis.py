from redis.asyncio import Redis
from settings import setting


redis = Redis(host=setting.REDIS_HOST, port=setting.REDIS_PORT)
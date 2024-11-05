import aioredis

REDIS_URL = "redis://redis:6379/0"

async def init_redis():
    return await aioredis.from_url(REDIS_URL)

async def close_redis(redis):
    await redis.close()

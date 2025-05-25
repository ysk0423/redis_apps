import aioredis
from quart import Quart


app = Quart(__name__)


# RedisおよびMySQL接続設定
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
STREAM_MAX_LEN = 1000

@app.before_serving
async def startup():
    app.redis = await aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
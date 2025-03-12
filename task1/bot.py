from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import Redis, RedisStorage


from task1.config import settings

redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
redis_storage = RedisStorage(redis=redis)

bot = Bot(settings.BOT_TOKEN)
dp = Dispatcher(storage=redis_storage)


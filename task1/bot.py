from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis

from task1.logger import logger
from task1.config import settings

redis_client = Redis.from_url(settings.REDIS_URL)
redis_storage = RedisStorage(redis=redis_client)


bot = Bot(settings.BOT_TOKEN)
dp = Dispatcher(storage=redis_storage)


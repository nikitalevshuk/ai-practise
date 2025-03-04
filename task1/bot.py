from aiogram import Bot, Dispatcher

from task1.config import bot_settings

bot = Bot(bot_settings.BOT_TOKEN)
dp = Dispatcher()


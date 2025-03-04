from aiogram import types, Dispatcher
from aiogram.filters import CommandStart
from task1.logger import logger
async def start_handler(message: types.Message):
    """Обработчик команды /start"""
    logger.info("Попали в start_handler")
    await message.answer("Привет! Отправь мне голосовое сообщение, и я обработаю его.")

def register_start_handler(dp: Dispatcher):
    dp.message.register(start_handler, CommandStart())
from aiogram import types, Dispatcher
from aiogram.filters import CommandStart

from task1.logger import logger
from task1.executor import executor_send_event

async def start_handler(message: types.Message):
    """Обработчик команды /start"""
    logger.info("Попали в start_handler")

    result = "Привет! Отправь мне голосовое сообщение, и я обработаю его."
    await message.answer(result)

    user_id = str(message.from_user.id)

    await executor_send_event(
        user_id=user_id,
        event_name="Start response",
        event_properties={"message": f"{result}"}
    )

def register_start_handler(dp: Dispatcher):
    """
    Загружает обработчик команды start в диспетчер
    """
    dp.message.register(start_handler, CommandStart())


import tempfile
import base64
import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

from task1.services.openai_api import get_mood_from_image
from task1.logger import logger
from task1.executor import executor_send_event

async def image_message_handler(message: Message, bot: Bot):
    """
    Обработчик изображений
    """
    logger.info("Попали в image_handler")
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)

    logger.info("Начали скачивание файла, передачу его в tempfile, а также декодирование")

    with tempfile.NamedTemporaryFile(delete=False) as temp_image:
        await bot.download_file(file.file_path, temp_image.name)
        photo_path = temp_image.name
        base64_image = base64.b64encode(temp_image.read()).decode("utf-8")

    logger.info("Успешно скачали и декодировали изображение!")

    result = await get_mood_from_image(base64_image)
    await message.answer(result)
    await asyncio.to_thread(os.remove, photo_path)

    user_id = str(message.from_user.id)
    await executor_send_event(
        user_id=user_id,
        event_name="Image response",
        event_properties={"message": f"{result}"}
    )

def register_image_handler(dp: Dispatcher):
    """
    Загружает обработчик изображений в диспетчер
    """
    dp.message.register(image_message_handler, F.photo)
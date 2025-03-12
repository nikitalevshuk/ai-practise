import os
import asyncio
import tempfile

from aiogram import F, Dispatcher, Bot
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext

from task1.services.openai_api import transcribe_audio, text_to_speech, ask_assistant
from task1.logger import logger
from task1.executor import executor_send_event

async def voice_message_handler(message: Message, bot: Bot, state: FSMContext):
    """
    Обработчик голосовых сообщений

    """
    logger.info("Попали в voice_handler")

    # получаем у message данные о голосе
    voice = message.voice

    # bot.get_file берет id файла и возвращает специальный тгшный объект файла, которые
    # качается через bot.download_file
    file = await bot.get_file(voice.file_id)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_audio:
        await bot.download_file(file.file_path, temp_audio.name)
        temp_audio_path = temp_audio.name

    text = await transcribe_audio(temp_audio_path)

    user_id = str(message.from_user.id)
    text_response = await ask_assistant(user_id, text, state)

    audio_path = await text_to_speech(text_response)

    audio_file = FSInputFile(audio_path)
    await message.answer_voice(voice=audio_file)
    await asyncio.to_thread(os.remove, audio_path)

    await executor_send_event(
        user_id=user_id,
        event_name="Voice response",
        event_properties={"message": f"{text_response}"}
    )

def register_voice_handler(dp: Dispatcher):
    """
    Загружает обработчик голосовых сообщений в диспетчер
    """
    dp.message.register(voice_message_handler, F.voice)
import os
import asyncio
import tempfile

from aiogram import F, Dispatcher, Bot
from aiogram.types import Message, FSInputFile

from task1.services.openai_api import transcribe_audio, text_to_speech, ask_assistant
from task1.logger import logger

async def voice_message_handler(message: Message, bot: Bot):
    """
    Обработчик голосовых сообщений
    1. Если при опросе диспетчер встретил голосовое сообщение, то мы попадаем в эту функцию(все
    потому что в декораторе прописано F.voice. F не имеет атрибута voice, мы пишем так потому что
    под капотом оно как то хитро устроено
    2. Загружаем в voice переменную message.voice, которая хранит в себе некоторую информацию о
    ГС(нам нужно file_id)
    3. bot.get_file возвращает объект file который тоже содержит в себе метаданные файла(но не сам
    файл)
    4. bot.download_file принимает путь файла на сервере телеграма и место куда его загрузить
    5. Мы создаем named temprorary file(named значит что он появляется не только как объект, но
    еще и в файловой системе, а значит другой процесс или функция сможет воспользоваться им) и
    загружаем в него наше голосовое сообщение
    6. Передаем наш файл с ГС в функцию которая конвертирует в текст и записываем ответ в text
    7. Через функцию спрашиваем assistant нашим text
    8. Записываем текстовый ответ от assistant
    9, Отправляем текстовый ответ в tts функцию и забираем от нее путь к звуковому файлу
    10. Используем конструктор класса FSInputFile чтобы обернуть наш файл приемлимым для тг образом
    11. Отправляем голосовое и удаляем tempfile
    """
    logger.info("Попали в voice_handler")
    voice = message.voice
    file = await bot.get_file(voice.file_id)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_audio:
        await bot.download_file(file.file_path, temp_audio.name)
        temp_audio_path = temp_audio.name

    text = await transcribe_audio(temp_audio_path)

    text_response = await ask_assistant(text)
    audio_path = await text_to_speech(text_response)

    audio_file = FSInputFile(audio_path)
    await message.answer_voice(voice=audio_file)
    await asyncio.to_thread(os.remove, audio_path)

def register_voice_handler(dp: Dispatcher):
    dp.message.register(voice_message_handler, F.voice)
import os
import openai
import tempfile
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, Voice
import asyncio

from config import bot_settings

bot = Bot(bot_settings.BOT_TOKEN)
dp = Dispatcher()

openai_client = openai.AsyncClient(api_key=bot_settings.OPENAI_API_KEY)

async def transcribe_audio(file_path: str):
    """
    Функция для распознавания речи с Whisper API
    1. Используем СИНХРОННЫЙ контекстный менеджер потому что open это синхронная операция, а если
    использовать асинхронный open то openai не проглотит объект audio_file
    2. Отправляем запрос на перевод из аудио у модели whisper-1 и передаем туда наш файл
    3. Записываем ответ в response и закрываем файл
    4. Удаляем файл(finally выполнится перед return)
    5. Возвращаем ответ

    """
    try:
        with open(file_path, "rb") as audio_file:
            response = await openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return response.text
    except openai.OpenAIError as e:
        return f"Ошибка OpenAI: {str(e)}"
    finally:
        try:
            await asyncio.to_thread(os.remove, file_path)
        except PermissionError:
            pass

@dp.message(F.voice)
async def voice_message_handler(message: Message):
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
    6. Передаем наш файл с ГС в функцию которая конвертирует в текст и возвращаем ответ.
    """
    voice = message.voice
    file = await bot.get_file(voice.file_id)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_audio:
        await bot.download_file(file.file_path, temp_audio.name)
        temp_audio_path = temp_audio.name

    text = await transcribe_audio(temp_audio_path)
    await message.answer(f"Ты сказал: {text}")

@dp.message(CommandStart())
async def start_handler(message: Message):
    """Обработчик команды /start"""
    await message.answer("Привет! Отправь мне голосовое сообщение, и я обработаю его.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

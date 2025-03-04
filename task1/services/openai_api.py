import asyncio
import os
import openai
import tempfile

from task1.config import bot_settings
from task1.logger import logger

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
    logger.info("Начался перевод из аудио в текст")
    try:
        with open(file_path, "rb") as audio_file:
            response = await openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return response.text
    except openai.OpenAIError as e:
        logger.critical(f"Ошибка OpenAI: {str(e)}")
    finally:
        try:
            await asyncio.to_thread(os.remove, file_path)
        except PermissionError:
            logger.critical("Произошла ошибка в ходе удаления файла в transcribe_audio")

async def ask_assistant(question: str):
    """
    Функция принимает строчный вопрос и отсылает его к AI ASSISTANT, и возвращает ответ
    1. Создаем поток(считай тоже самое что диалог)
    2. Создаем сообщение в нашем потоке от лица user`a
    3. Начинаем выполнять запрос
    4. Каждые две секунды обновляем статус запроса и ждем пока запрос либо обломается либо
    выполонится
    5. Если все норм то берем из потока всю переписку и выхватываем последнее сообщение
    6. Если с последним сообщением все ОК то возвращаем его
    """
    logger.info("Началась работа с Assistant")
    try:
        thread = await openai_client.beta.threads.create()
        thread_id = thread.id

        await openai_client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=f"{question}"
        )
        run = await openai_client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=bot_settings.OPENAI_ASSISTANT_ID
        )

        if run.status == "completed":
            messages = await openai_client.beta.threads.messages.list(thread_id=thread_id)
            last_message = messages.data[0]
            if last_message.role == "assistant":
                return last_message.content[0].text.value
        else:
            logger.critical("Ошибка: ассистент не смог обработать запрос.")

    except openai.OpenAIError as e:
        logger.critical(f"Ошибка OpenAI: {str(e)}")

async def text_to_speech(response_text: str):
    """
    Функция принимает текст и возвращает файл mp3
    1. Отправляем запрос на OpenAI API с текстом нашего голосового
    2. Переписываем файл ответа в наш временный файл и возвращаем путь к нему
    """
    logger.info("Началась работа TTS")
    try:
        response = await openai_client.audio.speech.create(
            model = "tts-1",
            voice = "alloy",
            input=response_text
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            audio_path = temp_audio.name
            temp_audio.write(response.read())

            return audio_path
    except openai.OpenAIError as e:
        logger.critical(f"Ошибка {e} в ходе перевода текста в голос")
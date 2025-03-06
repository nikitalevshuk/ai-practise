import asyncio
import json
import os
import openai
import tempfile

from task1.config import settings
from task1.logger import logger
from task1.database.db import session_factory
from task1.database.db_funcs import get_user_by_telegram_id, create_user
from task1.database.models import User

from sqlalchemy import update

openai_client = openai.AsyncClient(api_key=settings.OPENAI_API_KEY)

async def transcribe_audio(file_path: str):
    """
    Функция для распознавания речи с Whisper API

    """
    logger.info("Начался перевод из аудио в текст")
    try:
        with open(file_path, "rb") as audio_file:
            response = await openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        logger.info("Успешно перевели звук в текст и возвращаем его!")
        return response.text

    except Exception as e:
        logger.critical(f"Ошибка в ходе перевода аудио в текст: {str(e)}")

    finally:
        await asyncio.to_thread(os.remove, file_path)

async def ask_assistant(user_telegram_id: str, question: str):
    """
    Функция принимает строчный вопрос и отсылает его к AI ASSISTANT, который проверяет сообщение
    на присутствие информации о моральных ценностях пользователя. Если моральные ценности
    обнаружены, то произойдет запись в БД. В конечном итоге возвращает текстовый ответ от
    AI ASSISTANT. В ходе общение Assistant не подает виду что пытается обнаружить ценности
    пользователя

    """
    logger.info("Началось выполнение ask_assistant")

    async with session_factory() as db:
        logger.info("Запустили БД сессию")

        try:
            user = await get_user_by_telegram_id(db, user_telegram_id)
        except Exception as e:
            logger.critical(f"Ошибка в ходе получения пользователя по айдишнику: {str(e)}")
            return False

        try:
            logger.info("Получили user`a по telegram_id(может быть None)")
            if not user:
                logger.info("Пользователя с таким id не существует, создаем...")
                user = await create_user(
                    db,
                    user_telegram_id
                )
                logger.info("Пользователь создан")
        except Exception as e:
            logger.critical(f"Ошибка в ходе создания пользователя: {str(e)}")
            return False

        thread_id = user.thread_id

        if not thread_id:
            logger.info(f"У этого пользователя({user_telegram_id}) нет потока, создаем!")
            try:
                thread = await openai_client.beta.threads.create()
                user.thread_id, thread_id = thread.id, thread.id
                logger.info("Поток создан")
            except openai.OpenAIError as e:
                logger.info(f"Ошибка в ходе создания потока: {str(e)}")
                return False

        try:
            logger.info(f"Закидываем сообщение в поток, {question}")
            await openai_client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=f"{question}"
            )
            logger.info("Запускаем run в потоке и ждем пока все выполнится...")
            run = await openai_client.beta.threads.runs.create_and_poll(
                thread_id=thread_id,
                assistant_id=settings.OPENAI_ASSISTANT_ID
            )
        except openai.OpenAIError as e:
            logger.critical(f"Ошибка при отправлении сообщения и выполнении рана{str(e)}")

        tool_outputs = [] # переменная нужна исключительно для работы программы
        user_moral_values = "" # тут храним моральные ценности которые найдет assistant

        if run.required_action: # если есть какие то tools которые нужно обработать
            logger.info("Какие то функции вызвались и мы их обрабатываем")

            for tool in run.required_action.submit_tool_outputs.tool_calls:
                #этот кусок с tool_outputs нужен только чтобы получить нормальный run.status
                tool_outputs.append({
                    "tool_call_id": tool.id,
                    "output": ""
                })

                # если нашли в tools функцию которая определяет ценности то загружаем ее
                # атрибуты
                if tool.function.name == "define_core_values":
                    user_moral_values_dict = json.loads(tool.function.arguments)
                    user_moral_values = user_moral_values_dict["core_values"]
                    logger.info(f"Нашли в атрибутах функции следующие моральные ценности: "
                                f"{user_moral_values}")

                # тут мы закрываем работу с tools чтобы поменять run status
            try:
                run = await openai_client.beta.threads.runs.submit_tool_outputs_and_poll(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

                logger.info("Успешно выплюнули все функции, теперь run status пошел дальше")
            except Exception as e:
                logger.info(f"Ошибка пока выплевывали функции: {str(e)}")
        else:
            logger.info("Никаких функций assistant`a не вызвалось")

        try:
            if user_moral_values and user_moral_values not in user.values:
                # проверяем нормальные ли моральные ценности
                isvalid = await structured_output(user_moral_values)

                if isvalid:
                    #закидываем те ценности которые уже есть в БД и конвертируем в питон список
                    current_values = list(user.values)
                    #дубасим туда наши новые валидные ценности
                    current_values.append(user_moral_values)


                    logger.info(f"в бд должно быть: {current_values}")

                    stmt = update(User).where(User.telegram_user_id == user_telegram_id).values(values=current_values)
                    await db.execute(stmt)

        except Exception as e:
            logger.info(f"Ошибка в ходе проверки моральных ценностей: {str(e)}")

        try:
            if run.status == "completed":
                # достаем из потока последнее сообщение(оно по идее должно быть ответом ассистента)
                messages = await openai_client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]

                # если все четко то кидаем изменения в бд и отправляем текстовый ответ дальше
                # в voice handler
                if last_message.role == "assistant":
                    logger.info("Все четко, коммитим БД и возвращаем текст!")
                    await db.commit()
                    return last_message.content[0].text.value
            else:
                logger.critical("Ошибка: ассистент не смог обработать запрос, run status"
                                "почему то не completed")
                return False

        except openai.OpenAIError as e:
            logger.critical(f"Ошибка при попытке отправить ответ или закоммитить БД: {str(e)}")

async def text_to_speech(response_text: str):
    """
    Функция принимает текст и возвращает путь к файлу mp3

    """
    logger.info(f"Началась работа TTS, text {response_text}")
    try:
        logger.info("Отправилит запрос на OpenAI TTS")
        response = await openai_client.audio.speech.create(
            model = "tts-1",
            voice = "alloy",
            input=response_text
        )
    except openai.OpenAIError as e:
        logger.info(f"Ошибка в ходе отправки запроса на OpenAI TTS: {str(e)}")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            logger.info("Создаю временный файл и записываю в него ответ от OpenAI TTS(mp3)")
            audio_path = temp_audio.name
            temp_audio.write(response.read())

            logger.info("TTS завершает работу, вернув путь к файлу")
            return audio_path
    except Exception as e:
        logger.critical(f"Ошибка {str(e)} в ходе работы с файлами в text_to_speech")

async def structured_output(moral_values_to_check: str):
    """
    Функция проверяет, правильно ли определены ценности(они описаны в text) через completions API

    """
    logger.info("structured_output начинает работу")
    logger.info("отправляем запрос в chat.completions")

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role":"user", "content": f"Проверь следующие слова, они должны предоставлять"
            f" ценности, например семья, честность и подобное: {moral_values_to_check}"}
        ],
        functions=[{
            "name":"values",
             "description": "Проверяет, содержатся ли в сообщении моральные ценности или то"
                              " что любит человек",
            "parameters": {
                   "type": "object",
                  "properties": {
                    "valid": {
                        "type": "boolean",
                           "description": "True, если текст содержит моральные ценности, иначе False"
                    }
                  },
                 "required": ["valid"]
            }
        }],
    )

    logger.info("Парсим ответ от completions в dict")

    try:
        response_dict = json.loads(response.choices[0].message.function_call.arguments)
    except Exception as e:
        logger.info("Ошибка пока парсили ответ от completions, возвращаем False")
        return False

    is_valid = response_dict["valid"]

    logger.info(f"Возвращаем значение валидности: {is_valid}")
    return is_valid

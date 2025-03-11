import asyncio

from task1.services.openai_api import openai_client

tools = [
    {
        "type": "function",
        "function": {
            "name": "define_core_values",
            "description": "Если пользователь упоминает о своих моральных ценностях, запиши их",
            "parameters": {
                "type": "object",
                "properties": {
                    "core_values": {
                        "type": "string",
                        "description": "Моральные ценности пользователя"
                    }
                },
                "required": ["core_values"]
            }
        }
    }
]


async def files():
    """Создаёт vector_store и загружает в него файл."""
    vector_store = await openai_client.beta.vector_stores.create(name="Anxiety")

    file_paths = ["../../documents/anxiety.docx"]

    # Открываем файлы безопасно через with (чтобы они закрывались)
    file_streams = []
    try:
        for path in file_paths:
            file_streams.append(open(path, "rb"))

        # Загружаем файлы в vector_store
        await openai_client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=file_streams
        )
    finally:
        # Закрываем файлы после загрузки
        for file in file_streams:
            file.close()

    return vector_store


async def update_assistant():
    """Функция для изменения состояния assistant. В зависимости от нужды писать в ней разный код"""
    ...

if __name__ == "main":
    asyncio.run(update_assistant())
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

import asyncio

from config import bot_settings

bot = Bot(bot_settings.BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Привет! Отправь мне голосовое сообщение, и я обработаю его.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
from task1.handlers import register_handlers
from bot import bot, dp
from task1.logger import logger

async def main():
    logger.info("Бот запущен")
    register_handlers(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Бот упал с ошибкой {e}")

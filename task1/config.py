from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
load_dotenv()

class BotSettings(BaseSettings):
    """
    Тут находятся настройки которые относятся к моему тг боту
    Настройки подгружаются из переменных окружения, которые находятся в файле .env
    Через переменную model_config я показываю своему классу откуда подтягивать переменные
    без load_dotenv() SettingsConfigDict() не найдет мой файл .env
    """
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    OPENAI_API_KEY: str = os.getenv("OPENAI_ASSISTANT_ID")
    OPENAI_ASSISTANT_ID: str = os.getenv("OPENAI_API_KEY")

    class Config:
        env_file = ".env"

class DatabaseSettings(BaseSettings):
    """
    Тут мы храним настройки БДшки, ссылку создаем через property чтобы она генерировалась
    динамически
    """
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    class Config:
        env_file = ".env"

bot_settings = BotSettings()
db_settings = DatabaseSettings()


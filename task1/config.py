from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
load_dotenv()

class Settings(BaseSettings):
    """
    Тут находятся настройки которые относятся к моему тг боту
    Настройки подгружаются из переменных окружения, которые находятся в файле .env
    Через переменную model_config я показываю своему классу откуда подтягивать переменные
    без load_dotenv() SettingsConfigDict() не найдет мой файл .env
    """
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    OPENAI_API_KEY: str = os.getenv("OPENAI_ASSISTANT_ID")
    OPENAI_ASSISTANT_ID: str = os.getenv("OPENAI_API_KEY")
    AMPLITUDE_API_KEY: str = os.getenv("AMPLITUDE_API_KEY")

    class Config:
        env_file = ".env"

settings = Settings()


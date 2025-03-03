from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """
    Тут находятся настройки которые относятся к моему тг боту
    Настройки подгружаются из переменных окружения, которые находятся в файле .env
    Через переменную model_config я показываю своему классу откуда подтягивать переменные
    без load_dotenv() SettingsConfigDict() не найдет мой файл .env
    """
    BOT_TOKEN: str
    OPENAI_API_KEY: str
    OPENAI_ASSISTANT_ID: str

    class Config:
        env_file = ".env"

bot_settings = Settings()

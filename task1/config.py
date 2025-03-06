from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import ConfigDict

load_dotenv()

class BotSettings(BaseSettings):
    """
    Тут находятся настройки которые относятся к моему тг боту
    Настройки подгружаются из переменных окружения, которые находятся в файле .env
    Через переменную model_config я показываю своему классу откуда подтягивать переменные
    без load_dotenv() SettingsConfigDict() не найдет мой файл .env
    """
    BOT_TOKEN: str
    OPENAI_API_KEY: str
    OPENAI_ASSISTANT_ID: str

    model_config = ConfigDict(extra="ignore")

class DatabaseSettings(BaseSettings):
    """
    Тут мы храним настройки БДшки, ссылку создаем через property чтобы она генерировалась
    динамически
    """
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    @property
    def DATABASE_URL_asyncpg(self):
        return (
            f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}'
            f'@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )

    model_config = ConfigDict(extra="ignore")

bot_settings = BotSettings()
db_settings = DatabaseSettings()


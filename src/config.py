import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Загружаем .env файл с перезаписью существующих переменных
load_dotenv(override=True)


class Settings(BaseSettings):
    vk_group_token: str = os.getenv("VK_GROUP_TOKEN", "")
    yandex_music_token: str = os.getenv("YANDEX_MUSIC_TOKEN", "")

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()

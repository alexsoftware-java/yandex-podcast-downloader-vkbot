import logging

from vkbottle.bot import Bot

from src.config import settings
from src.bot.handlers import register_handlers
from src.yandex_music.client import ym_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    logger.info("Инициализация клиента Яндекс.Музыки...")
    ym_client.init(settings.yandex_music_token)
    logger.info("Клиент Яндекс.Музыки инициализирован.")

    bot = Bot(token=settings.vk_group_token)
    register_handlers(bot)

    logger.info("Запуск VK бота...")
    bot.run_forever()


if __name__ == "__main__":
    main()

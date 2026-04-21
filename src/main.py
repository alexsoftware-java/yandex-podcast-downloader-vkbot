import logging
import signal
import sys
import asyncio
from pathlib import Path
from logging.handlers import RotatingFileHandler

from vkbottle.bot import Bot

from src.config import settings
from src.bot.handlers import register_handlers
from src.yandex.client import ym_client
from src.yandex.player import player_manager

# Setup logging with rotation
def setup_logging():
    """Настройка логирования с ротацией файлов."""
    # Создаём папку для логов
    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Rotating file handler (10 MB, 5 backup files)
    file_handler = RotatingFileHandler(
        log_dir / "bot.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d > %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return logging.getLogger(__name__)


def validate_tokens():
    """Валидация токенов перед запуском."""
    logger = logging.getLogger(__name__)
    logger.info("Validating tokens...")
    
    # Validate VK token
    vk_token = settings.vk_group_token
    if not vk_token:
        raise ValueError("VK_GROUP_TOKEN is empty")
    if not vk_token.startswith("vk1.a."):
        logger.warning("VK token format looks incorrect (should start with 'vk1.a.')")
    
    # Validate Yandex token
    yandex_token = settings.yandex_music_token
    if not yandex_token:
        raise ValueError("YANDEX_MUSIC_TOKEN is empty")
    if not yandex_token.startswith("y0_"):
        logger.warning("Yandex token format looks incorrect (should start with 'y0_')")
    
    # Test Yandex token by getting account status
    try:
        from yandex_music import Client
        test_client = Client(yandex_token)
        test_client.init()
        # account_status() returns Status object, success means token is valid
        status = test_client.account_status()
        logger.info("Yandex token validated successfully")
    except Exception as e:
        logger.error("Yandex token validation failed: %s", e)
        raise ValueError(f"Invalid Yandex Music token: {e}")
    
    logger.info("Token validation completed")


# Global flag for shutdown
shutdown_flag = False


def signal_handler(signum, frame):
    """Обработчик сигналов остановки."""
    global shutdown_flag
    shutdown_flag = True
    logger = logging.getLogger(__name__)
    logger.info("Received signal %d, initiating graceful shutdown...", signum)


async def cleanup():
    """Очистка ресурсов при остановке."""
    logger = logging.getLogger(__name__)
    logger.info("Cleaning up resources...")
    
    # Close player manager DB
    try:
        await player_manager.close()
        logger.info("PlayerManager closed")
    except Exception as e:
        logger.error("Error closing PlayerManager: %s", e)
    
    logger.info("Cleanup completed")


def main():
    """Main entry point."""
    global shutdown_flag
    
    # Setup logging
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Starting Yandex Music Podcastr Parser — VK Bot")
    logger.info("=" * 60)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Validate tokens
        validate_tokens()
        
        # Initialize Yandex Music client
        logger.info("Initializing Yandex Music client...")
        ym_client.init(settings.yandex_music_token)
        logger.info("Yandex Music client initialized")
        
        # Initialize Player Manager (SQLite)
        logger.info("Initializing Player Manager (SQLite)...")
        loop = asyncio.new_event_loop()
        loop.run_until_complete(player_manager.init())
        logger.info("Player Manager initialized")
        
        # Create and configure bot
        logger.info("Creating VK Bot...")
        bot = Bot(token=settings.vk_group_token)
        register_handlers(bot)
        logger.info("VK Bot configured")
        
        # Run bot with graceful shutdown
        logger.info("Starting Bot Polling...")
        logger.info("Press Ctrl+C to stop")
        
        # Run in a task so we can monitor shutdown_flag
        import threading
        
        def run_bot():
            try:
                bot.run_forever()
            except Exception as e:
                logger.error("Bot error: %s", e)
                global shutdown_flag
                shutdown_flag = True
        
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        # Monitor shutdown flag
        import time
        while not shutdown_flag:
            time.sleep(1)
        
        logger.info("Shutting down...")
        
        # Graceful shutdown
        loop.run_until_complete(cleanup())
        
        logger.info("=" * 60)
        logger.info("Bot stopped gracefully")
        logger.info("=" * 60)
        
    except ValueError as e:
        logger.error("Configuration error: %s", e)
        sys.exit(1)
    except Exception as e:
        logger.exception("Fatal error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()

import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from vkbottle.bot import Bot, Message

from src.yandex.client import ym_client, DOWNLOADS_DIR
from src.yandex.player import player_manager
from src.bot.keyboard import create_podcast_keyboard, create_episodes_keyboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Executor для блокирующих операций
executor = ThreadPoolExecutor(max_workers=4)

# Временное хранилище результатов поиска (user_id -> список подкастов)
search_results_cache: dict[int, list] = {}

# Глобальная переменная для бота
bot_instance: Bot = None


def register_handlers(bot: Bot):
    """Регистрация всех обработчиков на боте."""
    global bot_instance
    bot_instance = bot

    @bot.on.message(text="/start")
    async def start_handler(message: Message):
        await player_manager.log_action(message.from_id, "command_start")
        await message.answer(
            "🎙 Добро пожаловать в бот подкастов Яндекс.Музыки!\n\n"
            "Отправьте название подкаста для поиска.\n"
            "Например: `Стиллавин` или `Аристокасты`"
        )

    @bot.on.message(text="/play")
    async def play_handler(message: Message):
        await player_manager.log_action(message.from_id, "command_play")
        state = player_manager.get_state(message.from_id)
        if not state.current_podcast_id:
            await message.answer("❌ Сначала найдите подкаст и выберите эпизод.")
            return
        await _send_current_episode(message)

    @bot.on.message(text="▶️ Play")
    async def play_button_handler(message: Message):
        await player_manager.log_action(message.from_id, "button_play")
        state = player_manager.get_state(message.from_id)
        if not state.current_podcast_id:
            await message.answer("❌ Сначала выберите подкаст.")
            return
        await _send_current_episode(message)

    @bot.on.message(text="⏭ Вперёд")
    async def next_episode_handler(message: Message):
        await player_manager.log_action(message.from_id, "button_next")
        episode = player_manager.next_episode(message.from_id)
        if not episode:
            await message.answer("❌ Нет доступных эпизодов.")
            return
        await message.answer(f"⏭ Следующий эпизод: **{episode['title']}**")
        await _send_episode_audio(message, episode)

    @bot.on.message(text="⏮ Назад")
    async def prev_episode_handler(message: Message):
        await player_manager.log_action(message.from_id, "button_prev")
        episode = player_manager.prev_episode(message.from_id)
        if not episode:
            await message.answer("❌ Нет доступных эпизодов.")
            return
        await message.answer(f"⏮ Предыдущий эпизод: **{episode['title']}**")
        await _send_episode_audio(message, episode)

    @bot.on.message(text="📋 Список эпизодов")
    async def episodes_list_handler(message: Message):
        await player_manager.log_action(message.from_id, "button_episodes")
        await _show_episodes_page(message)

    @bot.on.message(text="🔍 Новый поиск")
    async def new_search_handler(message: Message):
        await player_manager.log_action(message.from_id, "button_new_search")
        # Очищаем кэш поиска для этого пользователя
        if message.from_id in search_results_cache:
            del search_results_cache[message.from_id]
        # Сбрасываем состояние плеера
        state = player_manager.get_state(message.from_id)
        state.current_podcast_id = None
        state.current_podcast_title = None
        state.episodes = []
        state.current_episode_index = 0
        state.is_playing = False
        state.audio_file = None
        await player_manager._save_state(message.from_id)
        await message.answer("🔍 Введите название подкаста для поиска:")

    @bot.on.message(text="↩️ Назад к подкасту")
    async def back_to_podcast_handler(message: Message):
        await _show_episodes_page(message, show_back_button=False)

    @bot.on.message(text="⬅️ Пред.")
    async def prev_page_handler(message: Message):
        await player_manager.log_action(message.from_id, "button_prev_page")
        page = player_manager.prev_page(message.from_id)
        await _show_episodes_page(message, page=page)

    @bot.on.message(text="След. ➡️")
    async def next_page_handler(message: Message):
        await player_manager.log_action(message.from_id, "button_next_page")
        page = player_manager.next_page(message.from_id)
        await _show_episodes_page(message, page=page)

    @bot.on.message()
    async def default_handler(message: Message):
        """Обработчик всех сообщений — поиск подкастов и выбор."""
        text = message.text.strip()
        logger.info("Получено сообщение: %s от пользователя %d", text, message.from_id)

        # Игнорируем сообщения от самого бота
        if message.from_id <= 0:
            return

        # Если это число — проверяем, не выбор ли это эпизода или подкаста
        if text.isdigit():
            num = int(text)
            state = player_manager.get_state(message.from_id)

            # СНАЧАЛА проверяем выбор эпизода (если уже выбран подкаст)
            if state.episodes:
                # Вычисляем глобальный индекс эпизода
                global_index = state.episodes_page * state.episodes_per_page + (num - 1)
                if 0 <= global_index < len(state.episodes):
                    episode = state.episodes[global_index]
                    state.current_episode_index = global_index
                    await player_manager._save_state(message.from_id)
                    await player_manager.log_action(message.from_id, "select_episode", {"episode_id": episode["id"]})
                    await message.answer(f"▶️ Играю: **{episode['title']}**")
                    await _send_episode_audio(message, episode)
                    return

            # Если есть результаты поиска — это выбор подкаста
            if message.from_id in search_results_cache:
                results = search_results_cache[message.from_id]
                if 1 <= num <= len(results):
                    podcast = results[num - 1]
                    await player_manager.log_action(message.from_id, "select_podcast", {"podcast_id": podcast.id})
                    await _show_podcast_episodes(message, podcast)
                    return

            # Если ничего не найдено — пробуем как ID трека
            await player_manager.log_action(message.from_id, "select_track_by_id", {"track_id": text})
            await _send_episode_audio_by_id(message, text)
            return

        if text.startswith("/search"):
            query = text.split(maxsplit=1)[1] if len(text.split()) > 1 else ""
            if not query:
                await message.answer("❌ Введите запрос: `/search <название подкаста>`")
                return
        else:
            query = text

        await message.answer(f"🔍 Ищу подкасты по запросу: `{query}`...")
        await player_manager.log_action(message.from_id, "search", {"query": query})

        # Очищаем состояние плеера перед новым поиском
        state = player_manager.get_state(message.from_id)
        state.current_podcast_id = None
        state.current_podcast_title = None
        state.episodes = []
        state.current_episode_index = 0
        state.is_playing = False
        state.audio_file = None
        await player_manager._save_state(message.from_id)

        try:
            loop = asyncio.get_event_loop()
            logger.info("Выполняю поиск подкастов: %s", query)
            podcasts = await loop.run_in_executor(executor, ym_client.search_podcasts, query)
            logger.info("Результат поиска: %d подкастов", len(podcasts))
            
            if not podcasts:
                await message.answer("😔 Ничего не найдено. Попробуйте другой запрос.")
                return

            # Очищаем старый кэш перед записью нового
            if message.from_id in search_results_cache:
                del search_results_cache[message.from_id]

            # Сохраняем результаты в кэш
            search_results_cache[message.from_id] = podcasts

            # Показываем первые 3 результата
            for i, podcast in enumerate(podcasts[:3], 1):
                title = podcast.title or "Без названия"
                description = (podcast.short_description or podcast.description or "")[:200]
                track_count = podcast.track_count or 0

                msg = (
                    f"{i}. 📻 **{title}**\n"
                    f"📊 Эпизодов: {track_count}\n"
                    f"📝 {description}"
                )
                await message.answer(msg)

            if len(podcasts) > 3:
                await message.answer(f"... и ещё {len(podcasts) - 3} результатов.")
            
            await message.answer("\n📌 Отправьте номер подкаста (1-3) для выбора.")

        except Exception as e:
            logger.error("Ошибка при поиске: %s", e, exc_info=True)
            await message.answer(f"❌ Произошла ошибка при поиске: {e}")


async def _show_podcast_episodes(message: Message, podcast):
    """Показать эпизоды подкаста."""
    try:
        title = podcast.title or "Подкаст"
        
        await message.answer(f"⏳ Загружаю эпизоды: {title}...")
        
        loop = asyncio.get_event_loop()
        # Получаем эпизоды через поиск по названию
        episodes = await loop.run_in_executor(executor, ym_client.get_podcast_episodes, title, 50)
        
        if not episodes:
            await message.answer("❌ Не удалось загрузить эпизоды.")
            return
        
        # Сохраняем состояние
        await player_manager.set_podcast(message.from_id, str(podcast.id), title, episodes)
        
        await _show_episodes_page(message)
        
    except Exception as e:
        logger.error("Ошибка при загрузке эпизодов: %s", e, exc_info=True)
        await message.answer(f"❌ Ошибка: {e}")


async def _show_episodes_page(message: Message, page: int = None, show_back_button: bool = True):
    """Показать страницу эпизодов."""
    state = player_manager.get_state(message.from_id)
    if not state.episodes:
        await message.answer("❌ Нет доступных эпизодов.")
        return

    # Если передана страница, обновляем её
    if page is not None:
        state.episodes_page = page
        await player_manager._save_state(message.from_id)

    current_page = state.episodes_page
    total_pages = player_manager.get_total_pages(message.from_id)
    episodes = player_manager.get_episodes_page(message.from_id)

    # Определяем, какие кнопки показать
    has_prev = current_page > 0
    has_next = current_page < total_pages - 1
    
    # Объединяем все сообщения в одно
    episodes_list = "\n\n".join([
        f"{i}. **{episode['title']}** ({episode.get('duration', 0) // 60000 if episode.get('duration') else 0} мин)"
        for i, episode in enumerate(episodes, 1)
    ])
    
    # Сначала отправляем текст без клавиатуры
    await message.answer(
        f"📚 **{state.current_podcast_title}**\n"
        f"Страница {current_page + 1} из {total_pages}\n\n"
        f"Отправьте номер эпизода (1-5) для воспроизведения:\n\n"
        f"{episodes_list}"
    )
    
    # Затем отправляем клавиатуру отдельно
    keyboard = create_episodes_keyboard(current_page, total_pages)
    await message.answer(
        "🎧 Выберите эпизод или используйте навигацию:",
        keyboard=keyboard
    )


async def _send_current_episode(message: Message):
    state = player_manager.get_state(message.from_id)
    episode = player_manager.get_current_episode(message.from_id)
    if not episode:
        await message.answer("❌ Нет эпизодов для воспроизведения.")
        return
    await _send_episode_audio(message, episode)


async def _send_episode_audio(message: Message, episode: dict):
    """Скачать аудио и отправить пользователю."""
    try:
        track_id = episode.get("track_id") or episode.get("id")
        if not track_id:
            await message.answer("❌ Не удалось получить аудио для этого эпизода.")
            return

        await message.answer("⏳ Загружаю аудио...")

        loop = asyncio.get_event_loop()
        
        # Проверяем кэш
        cached_path = await player_manager.get_cached_audio(track_id)
        if cached_path and Path(cached_path).exists():
            logger.info("Using cached audio: %s", cached_path)
            audio_path = Path(cached_path)
        else:
            # Скачиваем напрямую по track_id
            audio_path = await loop.run_in_executor(
                executor,
                ym_client.download_audio,
                track_id,
                episode.get("title", "unknown")
            )
            if not audio_path:
                await message.answer("❌ Не удалось скачать аудио.")
                return
            
            # Кэшируем
            await player_manager.cache_audio(track_id, str(audio_path), episode.get("title", "unknown"))

        # Проверяем размер файла (VK ограничивает до 100 MB для документов)
        file_size = audio_path.stat().st_size
        file_size_mb = file_size / 1024 / 1024
        
        if file_size_mb > 100:
            await message.answer(f"❌ Файл слишком большой ({file_size_mb:.1f} MB). Максимум 100 MB.")
            return

        # Пробуем отправить как документ
        try:
            from vkbottle.tools import DocMessagesUploader

            uploader = DocMessagesUploader(bot_instance.api)
            attachment = await uploader.upload(audio_path)

            # Сначала отправляем аудио без клавиатуры
            await message.answer(
                f"🎧 **{episode['title']}** ({file_size_mb:.1f} MB)",
                attachment=attachment
            )

            # Получаем клавиатуру и отправляем отдельным сообщением
            state = player_manager.get_state(message.from_id)
            has_next = len(state.episodes) > 0 and state.current_episode_index < len(state.episodes) - 1
            has_prev = state.current_episode_index > 0
            keyboard = create_podcast_keyboard(has_next=has_next, has_prev=has_prev)

            await message.answer(
                "Используйте кнопки ниже для управления:",
                keyboard=keyboard
            )

            await player_manager.log_action(message.from_id, "audio_sent", {
                "track_id": track_id,
                "size_mb": file_size_mb,
                "cached": cached_path is not None
            })

            # Обновляем состояние после успешной отправки
            state = player_manager.get_state(message.from_id)
            state.audio_file = str(audio_path)
            state.is_playing = True
            await player_manager._save_state(message.from_id)

        except Exception as upload_error:
            # Если не получилось отправить как документ, отправляем как сообщение с путём
            logger.warning("Не удалось отправить как документ: %s. Отправляю как сообщение.", upload_error)

            # Сначала отправляем текст без клавиатуры
            await message.answer(
                f"🎧 **{episode['title']}** ({file_size_mb:.1f} MB)\n\n"
                f"📁 Файл сохранён локально:\n`{audio_path}`\n\n"
                f"❗️ Не удалось загрузить в VK (проверьте права сообщества).\n"
                f"Вы можете скопировать этот путь и открыть файл на компьютере."
            )

            # Обновляем состояние перед возвратом
            state = player_manager.get_state(message.from_id)
            state.audio_file = str(audio_path)
            state.is_playing = True
            await player_manager._save_state(message.from_id)
            
            return  # Пропускаем отправку клавиатуры из-за ошибки формата

    except Exception as e:
        logger.error("Ошибка при отправке аудио: %s", e, exc_info=True)
        await message.answer(f"❌ Произошла ошибка при загрузке аудио: {e}")


async def _send_episode_audio_by_id(message: Message, track_id: str):
    """Отправить аудио по ID трека."""
    try:
        await message.answer("⏳ Загружаю трек...")
        
        loop = asyncio.get_event_loop()
        tracks = await loop.run_in_executor(executor, ym_client._client.tracks, [int(track_id)])
        
        if not tracks or len(tracks) == 0:
            await message.answer("❌ Трек не найден.")
            return
        
        track = tracks[0]
        episode = {
            "id": track.id,
            "title": track.title or f"Трек {track.id}",
            "track_id": track.id,
        }
        
        await _send_episode_audio(message, episode)
        
    except Exception as e:
        logger.error("Ошибка при отправке трека: %s", e, exc_info=True)
        await message.answer("❌ Произошла ошибка при загрузке трека.")

import asyncio
import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, List, Dict
import aiosqlite

logger = logging.getLogger(__name__)


@dataclass
class PlayerState:
    """Состояние плеера для одного пользователя."""
    user_id: int
    current_podcast_id: Optional[str] = None
    current_podcast_title: Optional[str] = None
    current_episode_index: int = 0
    episodes: List[dict] = field(default_factory=list)
    is_playing: bool = False
    audio_file: Optional[str] = None
    episodes_page: int = 0
    episodes_per_page: int = 5

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return {
            "user_id": self.user_id,
            "current_podcast_id": self.current_podcast_id,
            "current_podcast_title": self.current_podcast_title,
            "current_episode_index": self.current_episode_index,
            "episodes": self.episodes,
            "is_playing": self.is_playing,
            "audio_file": str(self.audio_file) if self.audio_file else None,
            "episodes_page": self.episodes_page,
            "episodes_per_page": self.episodes_per_page,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PlayerState":
        """Create from dict."""
        return cls(
            user_id=data["user_id"],
            current_podcast_id=data.get("current_podcast_id"),
            current_podcast_title=data.get("current_podcast_title"),
            current_episode_index=data.get("current_episode_index", 0),
            episodes=data.get("episodes", []),
            is_playing=data.get("is_playing", False),
            audio_file=data.get("audio_file"),
            episodes_page=data.get("episodes_page", 0),
            episodes_per_page=data.get("episodes_per_page", 5),
        )


class PlayerManager:
    """Менеджер плеера с SQLite хранилищем."""

    def __init__(self, db_path: str = "data/state.db"):
        self.db_path = db_path
        self._states: Dict[int, PlayerState] = {}  # In-memory cache
        self._db: Optional[aiosqlite.Connection] = None
        self._init_lock = asyncio.Lock()

    async def init(self):
        """Инициализация базы данных."""
        async with self._init_lock:
            if self._db is None:
                Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
                self._db = await aiosqlite.connect(self.db_path)
                self._db.row_factory = aiosqlite.Row
                await self._create_tables()
                await self._load_states()
                logger.info("PlayerManager initialized with DB: %s", self.db_path)

    async def _create_tables(self):
        """Создание таблиц."""
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS player_states (
                user_id INTEGER PRIMARY KEY,
                state TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS audio_cache (
                track_id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                title TEXT,
                downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await self._db.commit()

    async def _load_states(self):
        """Загрузка состояний из БД."""
        async with self._db.execute("SELECT user_id, state FROM player_states") as cursor:
            async for row in cursor:
                try:
                    state_data = json.loads(row[1])
                    self._states[row[0]] = PlayerState.from_dict(state_data)
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning("Failed to load state for user %d: %s", row[0], e)

    async def _save_state(self, user_id: int):
        """Сохранение состояния пользователя в БД."""
        if user_id in self._states:
            state = self._states[user_id]
            state_json = json.dumps(state.to_dict(), ensure_ascii=False)
            await self._db.execute(
                """
                INSERT OR REPLACE INTO player_states (user_id, state, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                (user_id, state_json)
            )
            await self._db.commit()

    async def close(self):
        """Закрытие соединения с БД."""
        if self._db:
            await self._db.close()
            logger.info("PlayerManager DB closed")

    def get_state(self, user_id: int) -> PlayerState:
        """Получение состояния пользователя."""
        if user_id not in self._states:
            self._states[user_id] = PlayerState(user_id=user_id)
        return self._states[user_id]

    async def set_podcast(self, user_id: int, podcast_id: str, podcast_title: str, episodes: List[dict]):
        """Установка подкаста для пользователя."""
        state = self.get_state(user_id)
        state.current_podcast_id = podcast_id
        state.current_podcast_title = podcast_title
        state.episodes = episodes
        state.current_episode_index = 0
        state.episodes_page = 0
        state.is_playing = False
        await self._save_state(user_id)

    def next_episode(self, user_id: int) -> Optional[dict]:
        """Следующий эпизод."""
        state = self.get_state(user_id)
        if not state.episodes:
            return None
        state.current_episode_index = (state.current_episode_index + 1) % len(state.episodes)
        return state.episodes[state.current_episode_index]

    def prev_episode(self, user_id: int) -> Optional[dict]:
        """Предыдущий эпизод."""
        state = self.get_state(user_id)
        if not state.episodes:
            return None
        state.current_episode_index = (state.current_episode_index - 1) % len(state.episodes)
        return state.episodes[state.current_episode_index]

    def get_current_episode(self, user_id: int) -> Optional[dict]:
        """Текущий эпизод."""
        state = self.get_state(user_id)
        if not state.episodes:
            return None
        return state.episodes[state.current_episode_index]

    def get_episodes_page(self, user_id: int, page: int = None) -> List[dict]:
        """Получить страницу эпизодов."""
        state = self.get_state(user_id)
        if not state.episodes:
            return []

        if page is not None:
            state.episodes_page = page

        start = state.episodes_page * state.episodes_per_page
        end = start + state.episodes_per_page
        return state.episodes[start:end]

    def get_total_pages(self, user_id: int) -> int:
        """Получить общее количество страниц."""
        state = self.get_state(user_id)
        if not state.episodes:
            return 0
        return (len(state.episodes) - 1) // state.episodes_per_page + 1

    def next_page(self, user_id: int) -> int:
        """Перейти на следующую страницу."""
        state = self.get_state(user_id)
        total_pages = self.get_total_pages(user_id)
        if total_pages <= 1:
            return 0
        state.episodes_page = (state.episodes_page + 1) % total_pages
        return state.episodes_page

    def prev_page(self, user_id: int) -> int:
        """Перейти на предыдущую страницу."""
        state = self.get_state(user_id)
        total_pages = self.get_total_pages(user_id)
        if total_pages <= 1:
            return 0
        state.episodes_page = (state.episodes_page - 1) % total_pages
        return state.episodes_page

    # Statistics methods
    async def log_action(self, user_id: int, action: str, details: dict = None):
        """Логирование действия пользователя."""
        details_json = json.dumps(details, ensure_ascii=False) if details else None
        await self._db.execute(
            "INSERT INTO stats (user_id, action, details) VALUES (?, ?, ?)",
            (user_id, action, details_json)
        )
        await self._db.commit()

    async def get_stats(self, days: int = 7) -> dict:
        """Получение статистики за последние N дней."""
        async with self._db.execute(
            """
            SELECT action, COUNT(*) as count, COUNT(DISTINCT user_id) as unique_users
            FROM stats
            WHERE created_at >= datetime('now', ?)
            GROUP BY action
            """,
            (f"-{days} days",)
        ) as cursor:
            rows = await cursor.fetchall()
            return {row[0]: {"count": row[1], "unique_users": row[2]} for row in rows}

    # Audio cache methods
    async def get_cached_audio(self, track_id: str) -> Optional[str]:
        """Получить путь к кэшированному аудио."""
        async with self._db.execute(
            "SELECT file_path FROM audio_cache WHERE track_id = ?",
            (track_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

    async def cache_audio(self, track_id: str, file_path: str, title: str):
        """Кэширование аудио."""
        await self._db.execute(
            """
            INSERT OR REPLACE INTO audio_cache (track_id, file_path, title, downloaded_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (track_id, str(file_path), title)
        )
        await self._db.commit()


# Singleton instance
player_manager = PlayerManager()

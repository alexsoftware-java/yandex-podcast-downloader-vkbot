import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class PlayerState:
    """Состояние плеера для одного пользователя."""
    user_id: int
    current_podcast_id: Optional[str] = None
    current_podcast_title: Optional[str] = None
    current_episode_index: int = 0
    episodes: list[dict] = field(default_factory=list)
    is_playing: bool = False
    audio_file: Optional[Path] = None
    episodes_page: int = 0  # Текущая страница списка эпизодов
    episodes_per_page: int = 5  # Эпизодов на странице


class PlayerManager:
    """Менеджер плеера — хранит состояние для каждого пользователя."""

    def __init__(self):
        self._states: dict[int, PlayerState] = {}

    def get_state(self, user_id: int) -> PlayerState:
        if user_id not in self._states:
            self._states[user_id] = PlayerState(user_id=user_id)
        return self._states[user_id]

    def set_podcast(self, user_id: int, podcast_id: str, podcast_title: str, episodes: list[dict]):
        state = self.get_state(user_id)
        state.current_podcast_id = podcast_id
        state.current_podcast_title = podcast_title
        state.episodes = episodes
        state.current_episode_index = 0
        state.episodes_page = 0
        state.is_playing = False

    def next_episode(self, user_id: int) -> Optional[dict]:
        state = self.get_state(user_id)
        if not state.episodes:
            return None
        state.current_episode_index = (state.current_episode_index + 1) % len(state.episodes)
        return state.episodes[state.current_episode_index]

    def prev_episode(self, user_id: int) -> Optional[dict]:
        state = self.get_state(user_id)
        if not state.episodes:
            return None
        state.current_episode_index = (state.current_episode_index - 1) % len(state.episodes)
        return state.episodes[state.current_episode_index]

    def get_current_episode(self, user_id: int) -> Optional[dict]:
        state = self.get_state(user_id)
        if not state.episodes:
            return None
        return state.episodes[state.current_episode_index]

    def get_episodes_page(self, user_id: int, page: int = None) -> list[dict]:
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


player_manager = PlayerManager()

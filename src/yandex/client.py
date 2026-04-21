import logging
import tempfile
from pathlib import Path
from typing import Optional, List

from yandex_music import Client
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests

logger = logging.getLogger(__name__)

# Папка для загрузок
DOWNLOADS_DIR = Path("downloads")
DOWNLOADS_DIR.mkdir(exist_ok=True)


class YandexMusicClient:
    def __init__(self):
        self._client: Optional[Client] = None

    def init(self, token: str):
        """Инициализация клиента Яндекс.Музыки (синхронная)."""
        self._client = Client(token)
        self._client.init()
        logger.info("Yandex Music client initialized")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError)),
        reraise=True
    )
    def search_podcasts(self, query: str, limit: int = 10) -> List:
        """Поиск подкастов по запросу."""
        logger.debug("Searching podcasts: %s", query)
        results = self._client.search(query, type_="podcast", page=0)
        if not results or not results.podcasts or not results.podcasts.results:
            return []
        return results.podcasts.results[:limit]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError)),
        reraise=True
    )
    def get_podcast_episodes(self, podcast_name: str, count: int = 10) -> List[dict]:
        """Получение последних эпизодов подкаста через поиск по названию."""
        logger.debug("Getting episodes for: %s", podcast_name)
        results = self._client.search(podcast_name, type_="podcast_episode")
        if not results or not results.podcast_episodes or not results.podcast_episodes.results:
            return []

        episodes = []
        for ep in results.podcast_episodes.results[:count]:
            episodes.append({
                "id": ep.id,
                "title": ep.title or f"Эпизод {ep.id}",
                "description": ep.short_description or "",
                "duration": ep.duration_ms or 0,
                "track_id": ep.id,
            })
        return episodes

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError)),
        reraise=True
    )
    def get_episode_audio_url(self, track_id: str) -> Optional[str]:
        """Получение URL для скачивания аудио трека."""
        logger.debug("Getting audio URL for track: %s", track_id)
        tracks = self._client.tracks([track_id])
        if not tracks:
            return None
        track = tracks[0]
        
        # Получаем download info
        download_info = track.get_download_info()
        if not download_info or len(download_info) == 0:
            return None
        
        # Возвращаем URL из первого элемента (это объект DownloadInfo)
        first_info = download_info[0]
        if hasattr(first_info, "download_info_url"):
            return first_info.download_info_url
        return None

    def download_audio(self, track_id: str, title: str = "unknown") -> Optional[Path]:
        """Скачивание аудио-файла в папку downloads/ через track.download_bytes()."""
        try:
            logger.info("Downloading audio: %s (track_id: %s)", title, track_id)
            
            # Получаем трек
            tracks = self._client.tracks([track_id])
            if not tracks:
                logger.error("Track not found: %s", track_id)
                return None
            
            track = tracks[0]
            
            # Очищаем название для имени файла
            safe_title = "".join(c for c in title if c.isalnum() or c in " -_.").strip()[:50]
            filename = f"{safe_title}.mp3"
            file_path = DOWNLOADS_DIR / filename
            
            # Скачиваем через download_bytes
            logger.debug("Downloading %d bytes...", track.duration_ms)
            data = track.download_bytes()
            
            with open(file_path, "wb") as f:
                f.write(data)
            
            logger.info("Audio saved: %s (%d bytes)", file_path, len(data))
            return file_path
            
        except Exception as e:
            logger.error("Error downloading audio: %s", e, exc_info=True)
            return None

    def get_track_info(self, track_id: int) -> Optional[dict]:
        """Получение информации о треке."""
        try:
            tracks = self._client.tracks([track_id])
            if not tracks:
                return None
            track = tracks[0]
            return {
                "id": track.id,
                "title": track.title,
                "duration_ms": track.duration_ms,
                "available": track.available,
            }
        except Exception as e:
            logger.error("Error getting track info: %s", e)
            return None


# Singleton instance
ym_client = YandexMusicClient()

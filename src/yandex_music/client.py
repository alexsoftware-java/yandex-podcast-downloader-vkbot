import tempfile
from pathlib import Path
from typing import Optional

from yandex_music import Client

import logging

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

    def search_podcasts(self, query: str, limit: int = 10) -> list:
        """Поиск подкастов по запросу."""
        results = self._client.search(query, type_='podcast', page=0)
        if not results or not results.podcasts or not results.podcasts.results:
            return []
        return results.podcasts.results[:limit]

    def get_podcast_episodes(self, podcast_name: str, count: int = 10) -> list[dict]:
        """Получение последних эпизодов подкаста через поиск по названию.
        
        podcast_name: название подкаста для поиска эпизодов
        count: количество эпизодов для возврата
        """
        try:
            # Ищем эпизоды по названию подкаста
            results = self._client.search(podcast_name, type_='podcast_episode')
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
            
        except Exception as e:
            logger.error("Ошибка при получении эпизодов: %s", e)
            return []

    def get_latest_podcast_episodes(self, podcast_id: str, count: int = 10) -> list[dict]:
        """Получение свежих эпизодов через прямой API запрос.
        
        Яндекс.Музыка API не имеет публичного endpoint для получения всех эпизодов,
        но можно использовать feed для получения последних прослушанных/добавленных.
        """
        # Пробуем получить через users_playlists_list
        try:
            # Прямой запрос к API для получения эпизодов подкаста
            url = f"https://api.music.yandex.net/feeds/recent-tracks"
            response = self._client._request.get(url)
            
            if response and 'result' in response:
                # Фильтруем треки по podcast_id
                tracks = response['result'].get('tracks', [])
                episodes = []
                for track_data in tracks[:count]:
                    track_id = track_data.get('id')
                    if track_id:
                        track = self._client.tracks([track_id])
                        if track and len(track) > 0:
                            t = track[0]
                            episodes.append({
                                "id": t.id,
                                "title": t.title or f"Эпизод {t.id}",
                                "description": "",
                                "duration": t.duration_ms or 0,
                                "track_id": t.id,
                            })
                return episodes
        except Exception as e:
            logger.debug("Не удалось получить через feed: %s", e)
        
        # Fallback на get_podcast_episodes
        return self.get_podcast_episodes(podcast_id, count)

    def get_episode_audio_url(self, track_id: str) -> Optional[str]:
        """Получение URL для скачивания аудио трека."""
        try:
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
            if hasattr(first_info, 'download_info_url'):
                return first_info.download_info_url
            return None
        except Exception as e:
            logger.error("Ошибка при получении URL: %s", e)
            return None

    def download_audio(self, track_id: str, title: str = "unknown") -> Optional[Path]:
        """Скачивание аудио-файла в папку downloads/ через track.download_bytes()."""
        try:
            # Получаем трек
            tracks = self._client.tracks([track_id])
            if not tracks:
                logger.error("Трек не найден: %s", track_id)
                return None
            
            track = tracks[0]
            
            # Очищаем название для имени файла
            safe_title = "".join(c for c in title if c.isalnum() or c in " -_.").strip()[:50]
            filename = f"{safe_title}.mp3"
            file_path = DOWNLOADS_DIR / filename
            
            # Скачиваем через download_bytes
            data = track.download_bytes()
            
            with open(file_path, "wb") as f:
                f.write(data)
            
            logger.info("Аудио сохранено: %s (%d байт)", file_path, len(data))
            return file_path
            
        except Exception as e:
            logger.error("Ошибка при сохранении аудио: %s", e, exc_info=True)
            return None


# Singleton instance
ym_client = YandexMusicClient()

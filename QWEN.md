# Yandex Music Podcastr Parser — VK Bot

## Project Overview

A VKontakte (VK) messenger bot that allows users to search, browse, and listen to podcasts from Yandex Music. The bot downloads podcast episodes locally and sends them as voice messages or documents to users.

### Key Features
- Search podcasts by title using Yandex Music API
- Browse episodes with pagination (5 episodes per page)
- Play episodes via inline keyboard buttons or episode number selection
- Navigate between episodes (previous/next)
- Save audio files locally to `downloads/` folder
- Russian language interface for user interactions

### Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   VK Messenger  │────▶│   vkbottle Bot   │────▶│  Yandex Music   │
│   (User Input)  │     │  (Message Handler)│    │     API         │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  Player Manager  │
                        │  (State Storage) │
                        └──────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  downloads/      │
                        │  (Audio Files)   │
                        └──────────────────┘
```

## Project Structure

```
yandex-podcast-downloader-vkbot/
├── src/
│   ├── main.py              # Entry point, bot initialization
│   ├── config.py            # Settings via pydantic, env loading
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── handlers.py      # Message handlers, command routing
│   │   └── keyboard.py      # VK keyboard generation (dict format)
│   └── yandex_music/
│       ├── __init__.py
│       ├── client.py        # Yandex Music API wrapper
│       └── player.py        # Player state management per user
├── scripts/
│   └── get_yandex_token.py  # OAuth Device Flow token acquisition
├── downloads/               # Downloaded audio files (git-ignored)
├── .env                     # Environment variables (git-ignored)
├── .env.example             # Template for environment variables
├── .github/ISSUE_TEMPLATE/  # GitHub issue templates
├── pyproject.toml           # Project metadata and dependencies
├── requirements.txt         # pip dependencies
├── README.md                # Main documentation
├── CHANGELOG.md             # Version history
├── CONTRIBUTING.md          # Contribution guidelines
├── DEPLOY.md                # Deployment instructions
└── LICENSE                  # MIT License
```

## Building and Running

### Prerequisites
- Python 3.11 or higher
- VKontakte community with bot permissions
- Yandex Music account

### Installation

```bash
# Clone repository
git clone https://github.com/alexsoftware-java/yandex-podcast-downloader-vkbot.git
cd yandex-podcast-downloader-vkbot

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your tokens
```

### Environment Variables

| Variable | Description | How to Obtain |
|----------|-------------|---------------|
| `VK_GROUP_TOKEN` | VK community service key | VK Community → Manage → API Access → Create Key |
| `YANDEX_MUSIC_TOKEN` | Yandex Music access token | Run `python scripts/get_yandex_token.py` |

### Running the Bot

```bash
# Development
python -m src.main

# Or using pip install
pip install -e .
podcastr-bot
```

### Testing

```bash
# Run tests (if available)
pytest

# Linting
ruff check .
```

## Development Conventions

### Code Style
- **Formatting**: PEP 8 compliant
- **Type Hints**: Used throughout the codebase
- **Language**: 
  - Code comments: Russian
  - Documentation: English

### Project Patterns

1. **Singleton Pattern**: `ym_client` and `player_manager` are singletons
2. **Data Classes**: `PlayerState` uses `@dataclass` for state management
3. **Async/Sync Mix**: 
   - vkbottle handlers are async
   - Yandex Music API calls are sync (run in ThreadPoolExecutor)

### Key Components

#### `src/bot/handlers.py`
- Message routing via `@bot.on.message()` decorators
- Text-based commands: `/start`, `/search`, `/play`
- Button callbacks: `▶️ Play`, `⏭ Вперёд`, `⏮ Назад`, etc.
- Search results cached per user in `search_results_cache`

#### `src/yandex_music/client.py`
- Wrapper around `yandex_music.Client`
- Key methods:
  - `search_podcasts(query)` — search by title
  - `get_podcast_episodes(name, count)` — get episodes via search
  - `download_audio(track_id, title)` — download via `download_bytes()`

#### `src/yandex_music/player.py`
- `PlayerManager` — manages state per user (dict-based)
- `PlayerState` — dataclass with:
  - `current_podcast_id`, `current_podcast_title`
  - `episodes` list, `current_episode_index`
  - `episodes_page`, `episodes_per_page` (pagination)

#### `src/bot/keyboard.py`
- Returns VK API-compatible dict keyboards
- Functions:
  - `create_podcast_keyboard(has_next, has_prev)` — player controls
  - `create_episodes_keyboard(page, total_pages)` — episode selection

### State Management

User state is stored in-memory (dict):
```python
search_results_cache: dict[int, list] = {}  # user_id → podcasts
player_manager._states: dict[int, PlayerState] = {}  # user_id → state
```

**Note**: State is lost on restart. For production, consider Redis/SQLite.

### Error Handling

- Try/except blocks in all handlers
- Errors logged via `logging` module
- User-friendly error messages in Russian

### API Limitations

| Service | Limitation | Workaround |
|---------|------------|------------|
| VK | 100 MB file limit | Check file size before upload |
| VK | Document upload permissions | Fallback to local path message |
| Yandex Music | No direct episode list API | Search by podcast name + `type_='podcast_episode'` |

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| yandex-music | >=3.0.0 | Yandex Music API wrapper |
| vkbottle | >=4.3.0 | VK bot framework |
| pydantic-settings | >=2.0.0 | Settings management |
| python-dotenv | >=1.0.0 | .env file loading |
| requests | >=2.31.0 | HTTP requests (sync) |

## Repository

- **GitHub**: https://github.com/alexsoftware-java/yandex-podcast-downloader-vkbot
- **Issues**: https://github.com/alexsoftware-java/yandex-podcast-downloader-vkbot/issues
- **License**: MIT

## Quick Commands Reference

| User Input | Bot Response |
|------------|--------------|
| `/start` | Welcome message with instructions |
| `/search <query>` | Search results (up to 3 podcasts) |
| `1`, `2`, `3` | Select podcast or episode (context-aware) |
| `▶️ Play` | Play current episode |
| `⏭ Вперёд` | Next episode |
| `⏮ Назад` | Previous episode |
| `📋 Список эпизодов` | Show episodes list with pagination |
| `🔍 Новый поиск` | Clear state, start new search |
| `⬅️ Пред.` / `След. ➡️` | Navigate episode pages |

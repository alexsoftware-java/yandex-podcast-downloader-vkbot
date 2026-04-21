# Yandex Music Podcastr Parser — VK Bot

## 📋 Overview

VK bot for listening to Yandex Music podcasts.

## 🚀 Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Configure Tokens
1. Copy `.env.example` to `.env`
2. Get tokens:
   - **VK**: Manage Community → API Access → Create Key
   - **Yandex**: `python scripts/get_yandex_token.py`

### Run
```bash
python -m src.main
```

## 📁 Structure

```
yandex-podcast-downloader-vkbot/
├── src/
│   ├── main.py              # Entry point
│   ├── config.py            # Configuration
│   ├── bot/
│   │   ├── handlers.py      # Message handlers
│   │   └── keyboard.py      # Keyboard generation
│   └── yandex_music/
│       ├── client.py        # Yandex Music client
│       └── player.py        # Player manager
├── scripts/
│   └── get_yandex_token.py  # Token script
├── downloads/               # Downloaded audio
└── .env                     # Environment variables
```

## 🎮 Commands

- `/start` — Welcome message
- `/search <query>` — Search podcasts
- `▶️ Play` — Play current
- `⏭ Forward` / `⏮ Back` — Navigate
- `📋 Episodes List` — Show list
- `🔍 New Search` — Start over

## 🛠 Technologies

- Python 3.11+
- vkbottle 4.x
- yandex-music-api 3.x
- pydantic-settings

## 📝 License

MIT License

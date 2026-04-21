# 🎙 Yandex Music Podcastr Parser — VK Bot

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

VK bot for listening to Yandex Music podcasts via VKontakte messenger.

## 🚀 Features

- 🔍 **Search podcasts** by title
- 📚 **Browse episodes** with page navigation
- ▶️ **Play** via buttons or episode number
- ⏭⏮ **Navigate** between episodes
- 💾 **Save files** locally to `downloads/` folder
- ⌨️ **Convenient buttons** for control
- 🗄 **SQLite storage** — user state persists across restarts
- 💿 **Audio caching** — episodes downloaded once, reused for all users
- 📊 **Usage statistics** — track user actions and popular content
- 🔄 **Retry logic** — automatic retries for failed API requests
- 📝 **Rotating logs** — detailed logging with file rotation (10 MB)
- ⚡ **Graceful shutdown** — clean resource cleanup on stop

## 📋 Requirements

- Python 3.11 or higher
- VKontakte community with bot permissions
- Yandex Music account (Premium preferred for better quality)

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/alexsoftware-java/yandex-podcast-downloader-vkbot.git
cd yandex-podcast-downloader-vkbot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example file:
```bash
copy .env.example .env
```

Fill in the tokens in `.env`:

#### VK_GROUP_TOKEN
1. Open your VK community
2. **Manage** → **API Access**
3. **Create key** with permissions:
   - ✅ Manage community
   - ✅ Community messages
   - ✅ Access to photos
4. Copy the key (starts with `vk1.a....`)
5. Paste into `.env`: `VK_GROUP_TOKEN=vk1.a.XXXXX`

#### YANDEX_MUSIC_TOKEN
```bash
python scripts/get_yandex_token.py
```
1. Follow console instructions
2. Open the link in your browser
3. Enter confirmation code
4. Copy `access_token` to `.env`

## 🚀 Usage

### Start the bot

```bash
python -m src.main
```

After starting, write to your bot on VKontakte.

## 📬 How to Use

### Search for a podcast
Send the podcast title to the bot:
```
Стиллавин
```

Or use the command:
```
/search podcast
```

### Select a podcast
The bot will show a list of found podcasts. Send the number (1, 2, 3) to select.

### Select an episode
After selecting a podcast, the bot will show a list of episodes. Send the number (1-5) to play.

### Control
Use buttons:
- **⏮ Back / ⏭ Forward** — navigate between episodes
- **▶️ Play** — play current episode
- **📋 Episodes List** — show list
- **🔍 New Search** — start search again

## 📁 Project Structure

```
yandex-podcast-downloader-vkbot/
├── src/
│   ├── main.py              # Entry point
│   ├── config.py            # Configuration
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── handlers.py      # Message handlers
│   │   └── keyboard.py      # Keyboard generation
│   └── yandex_music/
│       ├── __init__.py
│       ├── client.py        # Yandex Music client
│       └── player.py        # Player manager
├── scripts/
│   └── get_yandex_token.py  # Token acquisition script
├── downloads/               # Downloaded audio files
├── .env                     # Environment variables
├── .env.example             # Example variables
├── .gitignore
├── pyproject.toml           # Python dependencies
├── requirements.txt
└── README.md
```

## 🛠 Technologies

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| VK Bot | [vkbottle](https://github.com/vkbottle/vkbottle) 4.x |
| Yandex Music | [yandex-music-api](https://github.com/MarshalX/yandex-music-api) |
| Configuration | pydantic-settings |
| HTTP | requests |

## ⚠️ Limitations

- **File size**: VK limits document uploads to 100 MB
- **Copyright**: Some podcasts may be unavailable for download
- **Premium**: Yandex Music Premium preferred for better audio quality

## 📝 License

MIT License — see [LICENSE](LICENSE) file

## 🤝 Contributing

1. Fork the repository
2. Create a branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

If you have questions or suggestions, create an [Issue](https://github.com/alexsoftware-java/yandex-podcast-downloader-vkbot/issues) in the repository.

---

**Made with ❤️ for podcast lovers**

# Changelog

All notable changes to this project.

## [1.1.0] - 2026-04-21

### Added
- 🗄 **SQLite storage** — User state persists across bot restarts (`data/state.db`)
- 💿 **Audio caching** — Episodes downloaded once, reused for all users
- 📊 **Usage statistics** — Track user actions, searches, and popular content
- 📝 **Rotating logs** — File logging with 10 MB rotation, 5 backup files
- ⚡ **Graceful shutdown** — Handle SIGINT/SIGTERM, clean resource cleanup
- 🔄 **Retry logic** — Automatic retries for API timeouts (3 attempts, exponential backoff)
- ✅ **Token validation** — Validate VK and Yandex tokens at startup

### Changed
- `PlayerManager` now uses async SQLite operations
- All user actions logged to database
- Improved error handling with tenacity library

### Fixed
- State loss on bot restart (now persisted)
- Redundant audio downloads (now cached)
- Silent token errors (now validated at startup)

### Technical
- New dependency: `aiosqlite>=0.20.0`
- New dependency: `tenacity>=8.2.0`
- New directory: `data/` for database and logs
- Updated `.gitignore` to exclude `data/`, `*.db`, `*.log`

## [1.0.0] - 2026-04-21

### Added
- 🔍 Search podcasts by title
- 📚 Browse episodes with page navigation
- ▶️ Play via buttons or episode number selection
- ⏭⏮ Navigate between episodes
- 💾 Save files locally to `downloads/` folder
- ⌨️ Convenient control buttons
- 🎤 Send audio as voice message or document
- 📦 Yandex Music token acquisition script

### Changed
- Updated dependencies to latest versions
- Improved error handling

### Fixed
- Fixed vkbottle 4.x import issues
- Fixed audio download via `download_bytes()`

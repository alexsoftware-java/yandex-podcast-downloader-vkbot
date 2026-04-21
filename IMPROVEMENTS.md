# Improvements Changelog

## Version 1.1.0 (2026-04-21) — Major Improvements

### 🗄 P0: Persistent Storage (SQLite)

**Problem:** User state was lost on bot restart (stored in-memory dict).

**Solution:** 
- Added SQLite database (`data/state.db`) for persistent storage
- `PlayerManager` now saves/loads user state from database
- States automatically restored on bot restart

**Files changed:**
- `src/yandex_music/player.py` — Complete rewrite with SQLite support
- `src/main.py` — Initialize PlayerManager DB on startup

**Database schema:**
```sql
CREATE TABLE player_states (
    user_id INTEGER PRIMARY KEY,
    state TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

### ✅ P0: Token Validation

**Problem:** Bot started with invalid tokens, errors only on first API call.

**Solution:**
- Validate tokens at startup before bot initialization
- Check VK token format (starts with `vk1.a.`)
- Check Yandex token format (starts with `y0_`)
- Test Yandex token by calling `account_status()`

**Files changed:**
- `src/main.py` — Added `validate_tokens()` function

---

### 💿 P1: Audio Caching

**Problem:** Same episode downloaded multiple times for different users.

**Solution:**
- Cache downloaded audio paths in SQLite (`audio_cache` table)
- Check cache before downloading
- Reuse cached files for all users

**Files changed:**
- `src/yandex_music/player.py` — Added `get_cached_audio()`, `cache_audio()`
- `src/bot/handlers.py` — Check cache before download

**Database schema:**
```sql
CREATE TABLE audio_cache (
    track_id TEXT PRIMARY KEY,
    file_path TEXT NOT NULL,
    title TEXT,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

### 📝 P1: Rotating Logging

**Problem:** Logs only to console, no file persistence.

**Solution:**
- RotatingFileHandler (10 MB, 5 backup files)
- Logs saved to `data/logs/bot.log`
- DEBUG level to file, INFO to console

**Files changed:**
- `src/main.py` — Added `setup_logging()` function

**Log format:**
```
2026-04-21 22:00:00 | INFO     | __main__:123 > Starting bot...
```

---

### ⚡ P1: Graceful Shutdown

**Problem:** Active downloads interrupted on bot stop.

**Solution:**
- Handle SIGINT/SIGTERM signals
- Wait for active tasks to complete
- Close database connections properly

**Files changed:**
- `src/main.py` — Added signal handlers, cleanup function

---

### 🗂 P2: Download Queues

**Status:** Partially implemented via ThreadPoolExecutor

**Current:** Uses ThreadPoolExecutor with 4 workers for blocking operations.

**Future improvement:** asyncio.Queue for ordered downloads.

---

### 🔄 P2: Retry Logic

**Problem:** API timeouts cause immediate failures.

**Solution:**
- tenacity library for retry logic
- 3 attempts with exponential backoff (2s, 4s, 8s max)
- Retry on Timeout and ConnectionError

**Files changed:**
- `src/yandex_music/client.py` — Added @retry decorators

**Example:**
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError))
)
def search_podcasts(self, query: str):
    # ...
```

---

### 📊 P2: Usage Statistics

**Problem:** No metrics on bot usage.

**Solution:**
- Log all user actions to `stats` table
- Track: commands, button clicks, searches, audio sent
- `get_stats()` method for reporting

**Files changed:**
- `src/yandex_music/player.py` — Added `log_action()`, `get_stats()`
- `src/bot/handlers.py` — Log all actions

**Database schema:**
```sql
CREATE TABLE stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Example stats query:**
```sql
SELECT action, COUNT(*) as count, COUNT(DISTINCT user_id) as unique_users
FROM stats
WHERE created_at >= datetime('now', '-7 days')
GROUP BY action
```

---

## Configuration

### New Files Created

```
data/
├── state.db          # User state storage
├── logs/
│   └── bot.log       # Rotating log file
└── stats.db          # Usage statistics (same as state.db)
```

### Updated Dependencies

```txt
aiosqlite>=0.20.0     # Async SQLite
tenacity>=8.2.0       # Retry logic
```

### Updated .gitignore

```
# Data and logs
data/
*.db
*.log
```

---

## Migration Guide

### From 1.0.0 to 1.1.0

1. **Install new dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create data directory:**
   ```bash
   mkdir data
   ```

3. **Run bot:**
   - Database tables created automatically
   - Old in-memory state lost (expected)
   - New state persisted automatically

4. **Check logs:**
   ```bash
   tail -f data/logs/bot.log
   ```

---

## Performance Improvements

| Metric | Before | After |
|--------|--------|-------|
| State persistence | ❌ None | ✅ SQLite |
| Audio download (repeat) | 🔄 Re-download | ✅ Cache hit |
| API timeout handling | ❌ Fail immediately | ✅ Retry 3x |
| Log retention | ❌ Console only | ✅ 50 MB (5 files) |
| Shutdown safety | ❌ Abrupt | ✅ Graceful |

---

## Future Improvements (Not Implemented)

- [ ] Redis instead of SQLite for multi-instance deployments
- [ ] asyncio.Queue for ordered download processing
- [ ] Admin commands (`/stats`, `/broadcast`)
- [ ] Web dashboard for statistics
- [ ] Scheduled cleanup of old cache files
- [ ] Rate limiting per user
- [ ] Premium-only features toggle

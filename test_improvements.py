#!/usr/bin/env python3
"""
Test script for verifying improvements.
Run: python test_improvements.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.yandex.player import PlayerManager


async def test_player_manager():
    """Test PlayerManager with SQLite."""
    print("Testing PlayerManager...")
    
    pm = PlayerManager("data/test_state.db")
    await pm.init()
    
    # Test set_podcast
    await pm.set_podcast(123, "podcast_1", "Test Podcast", [
        {"id": "1", "title": "Episode 1"},
        {"id": "2", "title": "Episode 2"},
    ])
    
    # Test get_state
    state = pm.get_state(123)
    assert state.current_podcast_title == "Test Podcast"
    assert len(state.episodes) == 2
    print("✅ set_podcast/get_state works")
    
    # Test pagination
    page = pm.get_episodes_page(123)
    assert len(page) == 2
    print("✅ get_episodes_page works")
    
    # Test log_action
    await pm.log_action(123, "test_action", {"key": "value"})
    print("✅ log_action works")
    
    # Test cache
    await pm.cache_audio("track_1", "/path/to/file.mp3", "Test Track")
    cached = await pm.get_cached_audio("track_1")
    assert cached == "/path/to/file.mp3"
    print("✅ cache_audio/get_cached_audio works")
    
    # Test stats
    stats = await pm.get_stats(7)
    print(f"✅ get_stats works: {stats}")
    
    # Cleanup
    await pm.close()
    Path("data/test_state.db").unlink(missing_ok=True)
    
    print("\n✅ All PlayerManager tests passed!")


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from src.yandex.client import ym_client
        print("✅ yandex.client imports")
    except Exception as e:
        print(f"❌ yandex.client import failed: {e}")
        return False
    
    try:
        from src.yandex.player import player_manager
        print("✅ yandex.player imports")
    except Exception as e:
        print(f"❌ yandex_music.player import failed: {e}")
        return False
    
    try:
        from src.bot.handlers import register_handlers
        print("✅ bot.handlers imports")
    except Exception as e:
        print(f"❌ bot.handlers import failed: {e}")
        return False
    
    try:
        from src.main import setup_logging, validate_tokens
        print("✅ main imports")
    except Exception as e:
        print(f"❌ main import failed: {e}")
        return False
    
    print("\n✅ All imports successful!")
    return True


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Yandex Music Podcastr Parser — Improvements Test")
    print("=" * 60)
    print()
    
    # Test imports
    if not test_imports():
        sys.exit(1)
    
    # Test PlayerManager
    await test_player_manager()
    
    print()
    print("=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

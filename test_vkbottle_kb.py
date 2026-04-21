#!/usr/bin/env python
"""Проверка совместимости с vkbottle."""
import sys
sys.path.insert(0, '.')

# Пытаемся создать keyboard через vkbottle API
from vkbottle.tools import Keyboard, KeyboardButtonColor


def test_keyboard_object():
    """Создание клавиатуры через vkbottle.Keyboard."""
    kb = Keyboard(one_time=True)
    
    # Добавляем кнопки
    kb.add_button("▶️ Play", payload='{"cmd": "play"}', color=KeyboardButtonColor.POSITIVE)
    kb.add_button("📋 Эпизоды", payload='{"cmd": "episodes"}', color=KeyboardButtonColor.DEFAULT)
    kb.add_simple_payload()  # Новая строка
    
    kb.add_button("🔍 Поиск", payload='{"cmd": "search"}', color=KeyboardButtonColor.SECONDARY)
    
    # Получаем JSON
    result = kb.get_json()
    
    print("vkbottle Keyboard:")
    print(result)
    print(f"\nType: {type(result)}")
    return result


if __name__ == "__main__":
    try:
        json_kb = test_keyboard_object()
        print("\n✅ vkbottle Keyboard работает!")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

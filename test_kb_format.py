#!/usr/bin/env python
"""Проверка формата клавиатуры для vkbottle."""
import sys
import json
sys.path.insert(0, '.')

from src.bot.keyboard import create_podcast_keyboard, create_episodes_keyboard


def test_vk_api_format():
    """Проверка соответствия формату VK API."""
    print("Проверка формата VK API...")
    
    kb = create_podcast_keyboard(has_next=True, has_prev=False)
    
    # Проверка структуры
    assert isinstance(kb, dict), "keyboard должен быть dict"
    assert "buttons" in kb, "обязательно поле 'buttons'"
    assert isinstance(kb["buttons"], list), "'buttons' должен быть списком"
    
    for i, row in enumerate(kb["buttons"]):
        assert isinstance(row, list), f"row[{i}] должен быть списком"
        for j, btn in enumerate(row):
            assert isinstance(btn, dict), f"btn[{i}][{j}] должен быть dict"
            assert "action" in btn, f"btn[{i}][{j}] имеет 'action'"
            assert isinstance(btn["action"], dict), "action должен быть dict"
            
            action = btn["action"]
            assert action.get("type") == "text", f"type должен быть 'text', got {action.get('type')}"
            assert "label" in action, "обязательно поле 'label'"
            assert "payload" in action, "обязательно поле 'payload'"
            
            # Проверка payload - должен быть строкой или JSON-объектом
            payload = action["payload"]
            if isinstance(payload, str):
                try:
                    parsed = json.loads(payload)
                    assert isinstance(parsed, dict), "payload должен быть JSON объектом"
                except json.JSONDecodeError:
                    raise AssertionError(f"payload не валидный JSON: {payload}")
            else:
                assert isinstance(payload, dict), "payload должен быть dict или строкой JSON"
    
    print("✅ Формат клавиатуры корректен!")
    return True


def test_color_values():
    """Проверка значений цветов (должны быть числами)."""
    print("\nПроверка значений цветов...")
    
    valid_colors = {0, 1, 2, 3, 4, 5}  # Цвета VK API
    
    kb = create_podcast_keyboard()
    for row in kb["buttons"]:
        for btn in row:
            color = btn.get("color")
            if color is not None:
                assert isinstance(color, int), f"color должен быть int, got {type(color)}"
                assert color in valid_colors, f"Неизвестный цвет: {color}"
    
    print("✅ Цвета корректны!")
    return True


def test_sample_output():
    """Вывод примера клавиатуры для отладки."""
    print("\nПример клавиатуры:")
    kb = create_podcast_keyboard(has_next=True, has_prev=True)
    print(json.dumps(kb, indent=2, ensure_ascii=False)[:500])
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТ ФОРМАТА КЛАВИАТУРЫ VK BOT")
    print("=" * 60)
    
    try:
        test_vk_api_format()
        test_color_values()
        test_sample_output()
        
        print("\n" + "=" * 60)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНУ!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

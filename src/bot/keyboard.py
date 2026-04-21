from vkbottle.tools import Keyboard, Text, ButtonColor


def create_podcast_keyboard(has_next: bool = True, has_prev: bool = False) -> dict:
    """Клавиатура управления плеером с навигацией. Возвращает dict для VK API."""
    keyboard = {
        "one_time": False,
        "inline": False,
        "buttons": []
    }
    
    buttons_row = []
    
    # Кнопки навигации по эпизодам
    if has_prev:
        buttons_row.append({
            "action": {"type": "text", "label": "⏮ Назад", "payload": "{\"cmd\": \"prev\"}"},
            "color": "secondary"
        })
    if has_next:
        buttons_row.append({
            "action": {"type": "text", "label": "⏭ Вперёд", "payload": "{\"cmd\": \"next\"}"},
            "color": "secondary"
        })
    
    if buttons_row:
        keyboard["buttons"].append(buttons_row)
    
    # Кнопки управления
    keyboard["buttons"].append([
        {
            "action": {"type": "text", "label": "▶️ Play", "payload": "{\"cmd\": \"play\"}"},
            "color": "positive"
        },
        {
            "action": {"type": "text", "label": "📋 Список эпизодов", "payload": "{\"cmd\": \"episodes\"}"},
            "color": "primary"
        }
    ])
    
    # Кнопка возврата к поиску
    keyboard["buttons"].append([
        {
            "action": {"type": "text", "label": "🔍 Новый поиск", "payload": "{\"cmd\": \"search\"}"},
            "color": "secondary"
        }
    ])
    
    return keyboard


def create_episodes_keyboard(current_page: int = 0, total_pages: int = 1) -> dict:
    """Клавиатура со списком эпизодов (номера 1-5)."""
    keyboard = {
        "one_time": False,
        "inline": False,
        "buttons": []
    }
    
    # Кнопки с номерами эпизодов
    numbers_row = []
    for i in range(1, 6):
        numbers_row.append({
            "action": {"type": "text", "label": str(i), "payload": f'{{"cmd": "episode_{i}"}}'},
            "color": "primary"
        })
    keyboard["buttons"].append(numbers_row)
    
    # Навигация по страницам
    if total_pages > 1:
        nav_row = []
        if current_page > 0:
            nav_row.append({
                "action": {"type": "text", "label": "⬅️ Пред.", "payload": "{\"cmd\": \"prev_page\"}"},
                "color": "secondary"
            })
        if current_page < total_pages - 1:
            nav_row.append({
                "action": {"type": "text", "label": "След. ➡️", "payload": "{\"cmd\": \"next_page\"}"},
                "color": "secondary"
            })
        if nav_row:
            keyboard["buttons"].append(nav_row)
    
    keyboard["buttons"].append([
        {
            "action": {"type": "text", "label": "↩️ Назад к подкасту", "payload": "{\"cmd\": \"back\"}"},
            "color": "secondary"
        }
    ])
    
    return keyboard

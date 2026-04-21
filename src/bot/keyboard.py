import json


def create_podcast_keyboard(has_next: bool = True, has_prev: bool = False) -> dict:
    """Клавиатура управления плеером с навигацией."""
    buttons = []

    # Кнопки навигации по эпизодам
    if has_prev or has_next:
        nav_buttons = []
        if has_prev:
            nav_buttons.append({
                "action": {"type": "text", "label": "⏮ Назад", "payload": json.dumps({"cmd": "prev"})}
            })
        if has_next:
            nav_buttons.append({
                "action": {"type": "text", "label": "⏭ Вперёд", "payload": json.dumps({"cmd": "next"})}
            })
        buttons.append(nav_buttons)

    # Кнопки управления
    buttons.append([
        {
            "action": {"type": "text", "label": "▶️ Play", "payload": json.dumps({"cmd": "play"})}
        },
        {
            "action": {"type": "text", "label": "📋 Список эпизодов", "payload": json.dumps({"cmd": "episodes"})}
        }
    ])

    # Кнопка возврата к поиску
    buttons.append([
        {
            "action": {"type": "text", "label": "🔍 Новый поиск", "payload": json.dumps({"cmd": "search"})}
        }
    ])

    return {"one_time": False, "inline": True, "buttons": buttons}


def create_episodes_keyboard(current_page: int = 0, total_pages: int = 1) -> dict:
    """Клавиатура со списком эпизодов (номера 1-5)."""
    buttons = []

    # Кнопки с номерами эпизодов (всегда 5 кнопок)
    numbers_row = []
    for i in range(1, 6):
        numbers_row.append({
            "action": {"type": "text", "label": str(i), "payload": json.dumps({"cmd": f"episode_{i}"})}
        })
    buttons.append(numbers_row)

    # Навигация по страницам
    has_prev = current_page > 0
    has_next = current_page < total_pages - 1
    
    if total_pages > 1 and (has_prev or has_next):
        nav_row = []
        if has_prev:
            nav_row.append({
                "action": {"type": "text", "label": "⬅️ Пред.", "payload": json.dumps({"cmd": "prev_page"})}
            })
        if has_next:
            nav_row.append({
                "action": {"type": "text", "label": "След. ➡️", "payload": json.dumps({"cmd": "next_page"})}
            })
        buttons.append(nav_row)

    # Кнопка возврата
    buttons.append([
        {
            "action": {"type": "text", "label": "↩️ Назад к подкасту", "payload": json.dumps({"cmd": "back"})}
        }
    ])

    return {"one_time": False, "inline": True, "buttons": buttons}

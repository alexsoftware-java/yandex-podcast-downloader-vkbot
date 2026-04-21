"""
Скрипт для получения токена Яндекс.Музыки через OAuth Device Flow.

Запустите этот скрипт, следуйте инструкциям в консоли,
затем скопируйте access_token в файл .env
"""

from yandex_music import Client


def on_code(code):
    """Вызывается когда получен код активации."""
    print("\n" + "=" * 50)
    print("ОТКРОЙТЕ В БРАУЗЕРЕ:")
    print(f"  {code.verification_url}")
    print("\nИ ВВЕДИТЕ КОД:")
    print(f"  {code.user_code}")
    print("=" * 50)
    print("\nПосле ввода кода в браузере нажмите Enter здесь...")
    input()


def main():
    print("🎵 Получение токена Яндекс.Музыки (OAuth Device Flow)")
    print()

    client = Client()
    
    print("Запрос кода активации...")
    token = client.device_auth(on_code=on_code)

    print("\n✅ Токен получен!")
    print("\n" + "=" * 50)
    print("Сохраните эти данные:")
    print("=" * 50)
    print(f"\nVK_GROUP_TOKEN=ваш_vk_токен")
    print(f"YANDEX_MUSIC_TOKEN={token.access_token}")
    print()
    print(f"# Refresh token (для обновления): {token.refresh_token}")
    print(f"# Истекает через (секунд): {token.expires_in}")
    print("=" * 50)
    print("\nТеперь вставьте YANDEX_MUSIC_TOKEN в файл .env")


if __name__ == "__main__":
    main()

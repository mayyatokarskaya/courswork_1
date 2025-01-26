import json
import os

from src.config import load_user_settings

# Путь к файлу настроек (относительно корня проекта)
settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../settings", "user_settings.json")


# Тестирование нормальной загрузки настроек
def test_load_user_settings_success():
    test_data = {"username": "testuser", "theme": "dark"}

    # Создаем тестовый JSON файл
    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(test_data, f)

    # Загружаем данные через функцию
    settings = load_user_settings("user_settings.json")

    # Проверяем, что данные совпадают
    assert settings == test_data


# Тестирование ошибки, когда файл не найден
def test_load_user_settings_file_not_found():
    # Удаляем файл перед тестом, чтобы симулировать его отсутствие
    if os.path.exists(settings_file):
        os.remove(settings_file)

    settings = load_user_settings("user_settings.json")

    # Проверяем, что вернулся пустой словарь
    assert settings == {}


# Тестирование ошибки формата JSON
def test_load_user_settings_json_decode_error():
    # Создаем поврежденный JSON файл
    with open(settings_file, "w", encoding="utf-8") as f:
        f.write("invalid json")

    settings = load_user_settings("user_settings.json")

    # Проверяем, что вернулся пустой словарь
    assert settings == {}

    # Восстанавливаем файл с правильным JSON
    valid_data = {"username": "testuser", "theme": "dark"}
    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(valid_data, f)

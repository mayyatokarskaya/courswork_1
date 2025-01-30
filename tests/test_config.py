import json
from unittest.mock import mock_open, patch

import pytest

from src.config import load_user_settings


# Тестирование нормальной загрузки настроек
def test_load_user_settings_success(tmp_path):
    test_data = {"username": "testuser", "theme": "dark"}

    # Создаем временный файл для тестов
    settings_file = tmp_path / "user_settings.json"

    # Записываем тестовые данные в файл
    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(test_data, f)

    # Загружаем данные через функцию
    settings = load_user_settings(str(settings_file))

    # Проверяем, что данные совпадают
    assert settings == test_data


# Тестирование ошибки, когда файл не найден
def test_load_user_settings_file_not_found(tmp_path):
    # Удаляем файл, если он существует, чтобы симулировать его отсутствие
    settings_file = tmp_path / "user_settings.json"
    if settings_file.exists():
        settings_file.unlink()

    settings = load_user_settings(str(settings_file))

    # Проверяем, что вернулся пустой словарь
    assert settings == {}


# Тестирование ошибки формата JSON
@pytest.fixture
def mock_file_path():
    """Фикстура для поддельного пути к файлу"""
    with patch("os.path.join", return_value="mocked_user_settings.json"):
        yield


def test_load_user_settings_json_decode_error(mock_file_path):
    # Подготовка поврежденного JSON
    invalid_json_content = "invalid json"

    # Мокаем функцию open для работы с поддельным файлом
    with patch("builtins.open", mock_open(read_data=invalid_json_content)) as mocked_file:
        # Тестируем функцию
        settings = load_user_settings("user_settings.json")

        # Проверяем, что функция вернула пустой словарь при ошибке декодирования JSON
        assert settings == {}

        # Убедимся, что файл открывался
        mocked_file.assert_called_once_with("mocked_user_settings.json", "r", encoding="utf-8")

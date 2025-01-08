import json
import os

def load_user_settings(settings_file="user_settings.json"):
    """Загрузка пользовательских настроек из файла JSON."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "settings", settings_file)

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Файл настроек {settings_file} не найден.")
        return {}
    except json.JSONDecodeError:
        print("Ошибка в формате JSON файла настроек.")
        return {}
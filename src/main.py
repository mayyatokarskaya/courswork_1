import json
import os.path

import pandas as pd
from src.views import process_data
from src.utils import load_excel
from src.services import fetch_currency_rates, fetch_stock_prices

def load_user_settings(settings_file="user_settings.json"):
    """Загрузка пользовательских настроек из файла JSON."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "settings", settings_file)

    #print(file_path)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Файл настроек {settings_file} не найден.")
        return {}
    except json.JSONDecodeError:
        print("Ошибка в формате JSON файла настроек.")
        return {}

def main():
    # Загружаем настройки пользователя
    user_settings = load_user_settings()

    # Получаем список валют и акций
    currencies = user_settings.get("user_currencies", [])
    stocks = user_settings.get("user_stocks", [])

    if not currencies or not stocks:
        print("Списки валют или акций не заданы в user_settings.json.")
        return

    # Загрузка данных
    file_path_2 = "data/operations.xlsx"
    transactions = load_excel(file_path_2)

    # Обработка данных и генерация отчета
    date_str = "2023-10-15"
    response = process_data(transactions, date_str, currencies, stocks)

    # Вывод результата
    print("JSON-ответ:")
    print(response)

if __name__ == "__main__":
    main()

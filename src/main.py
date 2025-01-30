import os

from src.config import load_user_settings
from src.utils import load_excel
from src.views import process_data


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
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Поднимаемся в корневую папку
        data_path = os.path.join(base_dir, "data", "operations.xlsx")  # Или operations.json
        data = load_excel(data_path)
    except FileNotFoundError as e:
        print(e)
        return

    # Обработка данных и генерация отчета
    date_str = "2021-12-31"
    response = process_data(data, date_str, currencies, stocks)

    # Проверяем и выводим результат
    print("JSON-ответ:")
    print(response)


if __name__ == "__main__":
    main()

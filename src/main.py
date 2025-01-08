from src.views import process_data
from src.utils import load_excel
from src.config import load_user_settings  # Импортируем функцию из config.py

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
        data = load_excel("../data/operations.xlsx")  # Убедитесь, что путь к файлу корректен
    except FileNotFoundError as e:
        print(e)
        return

    # Обработка данных и генерация отчета
    date_str = "2021-12-31"  # Используем дату из operations.xlsx
    response = process_data(data, date_str, currencies, stocks)

    # Проверяем и выводим результат
    print("JSON-ответ:")
    print(response)

if __name__ == "__main__":
    main()

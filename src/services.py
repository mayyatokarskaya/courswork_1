import os
import json
import logging
import pandas as pd

# Устанавливаем конфигурацию для логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PATH = os.path.join(BASE_DIR, "data", "operations.xlsx")


def analyze_cashback_categories(data, year, month):
    """Анализирует категории повышенного кешбэка за указанный месяц и год"""
    try:
        # проверка, что нужные столбцы есть
        required_columns = {"Дата операции", "Категория", "Сумма операции"}
        if not required_columns.issubset(data.columns):
            raise ValueError(f"Отсутствуют обязательные столбцы: {required_columns - set(data.columns)}")

        # Обработка даты
        data["Дата операции"] = pd.to_datetime(data["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")

        # Удаляем записи с некорректной датой
        data = data.dropna(subset=["Дата операции"])

        # Фильтруем данные по указанным году и месяцу
        filtered_data = data[(data["Дата операции"].dt.year == year) & (data["Дата операции"].dt.month == month)]

        if filtered_data.empty:
            logging.info("Нет данных для указанного месяца и года.")
            return json.dumps({}, ensure_ascii=False, indent=4)

        # Группируем суммы кешбэка по категориям
        category_cashback = (
            filtered_data.groupby("Категория")["Сумма операции"].sum().apply(lambda x: x * 0.05).to_dict()
        )

        logging.info("Анализ категорий завершен.")

        return json.dumps(category_cashback, ensure_ascii=False, indent=4)

    except Exception as e:
        logging.error(f"Ошибка анализа кешбэка: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False, indent=4)


def find_transfers_to_individuals(file_path=FILE_PATH):
    """Поиск переводов физическим лицам"""
    try:
        data = pd.read_excel(file_path)

        required_columns = {"Категория", "Описание"}
        if not required_columns.issubset(data.columns):
            raise ValueError(f"Отсутствуют обязательные столбцы: {required_columns - set(data.columns)}")

        regex = r"[А-ЯЁ][а-яё]+ [А-Я]\."
        transfers = data[(data["Категория"] == "Переводы") & (data["Описание"].str.contains(regex, na=False))]

        # Преобразуем результат в JSON
        result = transfers.to_dict(orient="records")

        # Логируем результат
        logging.info(f"Найдено переводов физическим лицам: {len(result)}.")

        return json.dumps(result, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Ошибка поиска переводов: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    # Загружаем данные из файла Excel
    try:
        data = pd.read_excel("../data/operations.xlsx")  # Убедитесь, что путь к файлу корректный
    except FileNotFoundError as e:
        logging.error(f"Файл не найден: {e}")
        data = None

    if data is not None:
        # Анализ кешбэка за декабрь 2021
        cashback_result = analyze_cashback_categories(data, year=2021, month=12)
        print("Результат анализа кешбэка:")
        print(cashback_result)

# Поиск переводов физлицам
transfers_result = find_transfers_to_individuals()
print("Результат поиска переводов физлицам:")
print(transfers_result)

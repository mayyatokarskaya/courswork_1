import os
import json
import logging
import pandas as pd

# Устанавливаем конфигурацию для логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PATH = os.path.join(BASE_DIR, "data", "operations.xlsx")


def analyze_cashback_categories(data, year, month, cashback_threshold=100):
    """
    Анализирует категории с повышенным кешбэком за указанный месяц и год.

    :param data: DataFrame с данными о транзакциях.
    :param year: Год для анализа.
    :param month: Месяц для анализа.
    :param cashback_threshold: Порог для определения повышенного кешбэка (по умолчанию 100 рублей).
    :return: JSON с категориями и суммарным кешбэком.
    """
    try:
        # Проверка наличия обязательных столбцов
        required_columns = {"Дата операции", "Категория", "Кэшбэк"}
        if not required_columns.issubset(data.columns):
            raise ValueError(f"Отсутствуют обязательные столбцы: {required_columns - set(data.columns)}")

        # Преобразуем дату
        data["Дата операции"] = pd.to_datetime(data["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")

        # Удаляем записи с некорректной датой
        data = data.dropna(subset=["Дата операции"])

        # Фильтруем данные по указанным году и месяцу
        filtered_data = data[(data["Дата операции"].dt.year == year) & (data["Дата операции"].dt.month == month)]

        if filtered_data.empty:
            logging.info("Нет данных для указанного месяца и года.")
            return json.dumps({}, ensure_ascii=False, indent=4)

        # Группируем данные по категориям и суммируем кешбэк
        category_cashback = (
            filtered_data.groupby("Категория")["Кэшбэк"]
            .sum()
            .reset_index()
        )

        # Определяем категории с повышенным кешбэком
        high_cashback_categories = category_cashback[category_cashback["Кэшбэк"] > cashback_threshold]

        # Преобразуем результат в словарь
        result = high_cashback_categories.set_index("Категория")["Кэшбэк"].to_dict()

        logging.info(f"Категории с повышенным кешбэком: {result}")
        return json.dumps(result, ensure_ascii=False, indent=4)

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

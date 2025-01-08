import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
from src.utils import load_excel

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Декоратор для сохранения отчетов в файл
def save_report(file_name: Optional[str] = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Определяем имя файла для сохранения
            if not file_name:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                reports_dir = os.path.join(base_dir, "report")
                if not os.path.exists(reports_dir):
                    os.makedirs(reports_dir)
                file_name_to_save = os.path.join(reports_dir, f"report_{func.__name__}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                reports_dir = os.path.join(base_dir, "report")
                if not os.path.exists(reports_dir):
                    os.makedirs(reports_dir)
                file_name_to_save = os.path.join(reports_dir, file_name)

            # Сохраняем отчет в файл
            with open(file_name_to_save, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            logging.info(f"Отчет сохранен в файл: {file_name_to_save}")

            return result

        return wrapper

    return decorator

@save_report()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> dict:
    """
    Рассчитывает траты по категории за последние три месяца от переданной даты.

    :param transactions: DataFrame с транзакциями
    :param category: Название категории
    :param date: Опциональная дата в формате YYYY-MM-DD. Если не передана, берется текущая дата.
    :return: Словарь с тратами по категории за последние три месяца
    """
    try:
        # Устанавливаем текущую дату, если не передана
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        date = datetime.strptime(date, "%Y-%m-%d")
        three_months_ago = date - timedelta(days=90)

        # Фильтруем транзакции по категории и дате
        filtered_data = transactions[
            (transactions["Категория"] == category) &
            (transactions["Дата операции"] >= three_months_ago) &
            (transactions["Дата операции"] <= date)
        ]

        # Рассчитываем общую сумму трат
        total_spent = filtered_data["Сумма операции"].sum()

        result = {
            "category": category,
            "total_spent": round(total_spent, 2),
            "from_date": three_months_ago.strftime("%Y-%m-%d"),
            "to_date": date.strftime("%Y-%m-%d")
        }

        logging.info("Отчет по категории успешно сформирован.")
        return result

    except Exception as e:
        logging.error(f"Ошибка при формировании отчета по категории: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Загружаем данные из файла
    try:
        transactions = load_excel("operations.xlsx")
    except FileNotFoundError as e:
        logging.error(e)
        exit(1)

    # Преобразуем дату операции в формат datetime
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")

    # Указываем дату для отчета
    specific_date = "2021-03-26"

    # Генерируем отчет по категории "Продукты" с указанной датой
    spending_by_category(transactions, "Фастфуд", specific_date)



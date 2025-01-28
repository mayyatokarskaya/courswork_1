import json
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from src.utils import load_excel


# Декоратор для сохранения отчетов в файл
def save_report(file_name: Optional[str] = None, reports_dir: Optional[str] = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Определяем директорию для сохранения
            if reports_dir is None:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                reports_dir_to_use = os.path.join(base_dir, "report")
            else:
                reports_dir_to_use = reports_dir

            # Создаем директорию, если она не существует
            if not os.path.exists(reports_dir_to_use):
                os.makedirs(reports_dir_to_use)

            # Определяем имя файла для сохранения
            if not file_name:
                file_name_to_save = os.path.join(reports_dir_to_use, f"report_{func.__name__}.json")
            else:
                file_name_to_save = os.path.join(reports_dir_to_use, file_name)

            # Сохраняем отчет в файл
            with open(file_name_to_save, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            logging.info(f"Отчет сохранен в файл: {file_name_to_save}")

            return result

        return wrapper

    return decorator


@save_report()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> dict:
    """Рассчитывает траты по категории за последние три месяца от переданной даты"""
    try:
        current_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()

        # Вычисляем дату начала трехмесячного периода (первый день месяца, который был три месяца назад)
        three_months_ago = (current_date.replace(day=1) - timedelta(days=90)).replace(day=1)

        # Фильтруем транзакции по категории и дате
        filtered_data = transactions[
            (transactions["Категория"] == category)
            & (transactions["Дата операции"] >= three_months_ago)
            & (transactions["Дата операции"] <= current_date)
        ]

        # Рассчитываем общую сумму трат и преобразуем в стандартный тип Python
        total_spent = filtered_data["Сумма операции"].sum().item()

        result = {
            "category": category,
            "total_spent": round(total_spent, 2),
            "from_date": three_months_ago.strftime("%Y-%m-%d"),
            "to_date": current_date.strftime("%Y-%m-%d"),
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
    transactions["Дата операции"] = pd.to_datetime(
        transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
    )

    report_date = "2021-12-31"
    # Генерируем отчет по категории "РЖД" на указанную дату
    result = spending_by_category(transactions, category="Супермаркеты", date=report_date)

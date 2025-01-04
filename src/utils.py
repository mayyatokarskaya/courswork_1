import os

import pandas as pd
from datetime import datetime

def load_excel(file_name = "operations.xlsx") -> pd.DataFrame:
    """Загрузка данных из Excel."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "data", file_name)

    print(file_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден. Проверьте путь к файлу и его наличие")

    return pd.read_excel(file_path)

def filter_data_by_date(dataframe: pd.DataFrame, date_str: str) -> pd.DataFrame:
    """Фильтрация данных с начала месяца до указанной даты."""
    input_date = datetime.strptime(date_str, "%Y-%m-%d")
    start_of_month = input_date.replace(day=1)
    dataframe["Дата операции"] = pd.to_datetime(dataframe["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    return dataframe[(dataframe["Дата операции"] >= start_of_month) & (dataframe["Дата операции"] <= input_date)]

def calculate_card_expenses(transactions):
    """Рассчитывает общую сумму расходов и кешбэк для каждой карты."""
    cards = transactions.groupby("card_last_4_digits").agg(
        total_spent=("amount", "sum")
    ).reset_index()
    cards["cashback"] = (cards["total_spent"] // 100).round(2)
    return cards.to_dict(orient="records")

def get_top_transactions(transactions, n=5):
    """Определяет топ-N транзакций по сумме."""
    top_transactions = transactions.sort_values("amount", ascending=False).head(n)
    return top_transactions.to_dict(orient="records")

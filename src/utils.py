import os
from datetime import datetime

import pandas as pd


def load_excel(file_name: str = "operations.xlsx") -> pd.DataFrame:
    """Загрузка данных из Excel.

    :param file_name: Имя файла Excel.
    :return: DataFrame с данными из файла.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "data", file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден. Проверьте путь к файлу и его наличие")

    return pd.read_excel(file_path)


def filter_data_by_date(dataframe: pd.DataFrame, date_str: str) -> pd.DataFrame:
    """Фильтрация данных с начала месяца до указанной даты.

    :param dataframe: DataFrame с данными.
    :param date_str: Дата в формате YYYY-MM-DD.
    :return: Отфильтрованный DataFrame.
    """
    try:
        input_date = datetime.strptime(date_str, "%Y-%m-%d")
        start_of_month = input_date.replace(day=1)
        dataframe["Дата операции"] = pd.to_datetime(
            dataframe["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
        )

        # Фильтруем данные по диапазону дат
        filtered_data = dataframe[
            (dataframe["Дата операции"] >= start_of_month) & (dataframe["Дата операции"] <= input_date)
        ]

        # Удаляем строки с некорректными датами
        return filtered_data.dropna(subset=["Дата операции"])
    except Exception as e:
        raise ValueError(f"Ошибка при фильтрации данных по дате: {e}")


def calculate_card_expenses(transactions: pd.DataFrame) -> list[dict]:
    """Рассчитывает общую сумму расходов и кешбэк для каждой карты.

    :param transactions: DataFrame с транзакциями.
    :return: Список словарей с расходами и кешбэком по картам.
    """
    required_columns = ["Номер карты", "Сумма операции"]
    if not all(col in transactions.columns for col in required_columns):
        raise ValueError(f"Отсутствуют необходимые столбцы: {required_columns}")

    transactions = transactions.dropna(subset=["Номер карты"]).copy()
    transactions["last_4_digits"] = transactions["Номер карты"].astype(str).str.extract(r"\*(\d{4})")[0]

    if not pd.api.types.is_numeric_dtype(transactions["Сумма операции"]):
        transactions["Сумма операции"] = pd.to_numeric(
            transactions["Сумма операции"].str.replace(",", ".", regex=False), errors="coerce"
        )

    transactions = transactions.dropna(subset=["Сумма операции"])

    cards = transactions.groupby("last_4_digits").agg(total_spent=("Сумма операции", "sum")).reset_index()

    cards["cashback"] = (cards["total_spent"] / 100).round(2)
    return cards.to_dict(orient="records")


def get_top_transactions(transactions: pd.DataFrame, n: int = 5) -> list[dict]:
    """Определяет топ-N транзакций по сумме платежа.

    :param transactions: DataFrame с транзакциями.
    :param n: Количество транзакций в топе.
    :return: Список словарей с топ-N транзакциями.
    """
    required_columns = ["Сумма платежа", "Дата операции"]
    if not all(col in transactions.columns for col in required_columns):
        raise ValueError(f"Отсутствуют необходимые столбцы: {required_columns}")

    if not pd.api.types.is_numeric_dtype(transactions["Сумма платежа"]):
        transactions["Сумма платежа"] = pd.to_numeric(
            transactions["Сумма платежа"].str.replace(",", ".", regex=False), errors="coerce"
        )

    transactions = transactions.dropna(subset=["Сумма платежа"])
    top_transactions = transactions.sort_values("Сумма платежа", ascending=False).head(n)

    top_transactions["Дата операции"] = top_transactions["Дата операции"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return top_transactions.to_dict(orient="records")

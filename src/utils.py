import os
import pandas as pd
from datetime import datetime

def load_excel(file_name="operations.xlsx") -> pd.DataFrame:
    """Загрузка данных из Excel."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "data", file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден. Проверьте путь к файлу и его наличие")

    return pd.read_excel(file_path)

def filter_data_by_date(dataframe: pd.DataFrame, date_str: str) -> pd.DataFrame:
    """Фильтрация данных с начала месяца до указанной даты."""
    try:
        input_date = datetime.strptime(date_str, "%Y-%m-%d")
        start_of_month = input_date.replace(day=1)
        dataframe["Дата операции"] = pd.to_datetime(dataframe["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
        filtered_data = dataframe[(dataframe["Дата операции"] >= start_of_month) & (dataframe["Дата операции"] <= input_date)]
        return filtered_data.dropna(subset=["Дата операции"])  # Удаляем строки с некорректными датами
    except Exception as e:
        print(f"Ошибка при фильтрации данных по дате: {e}")
        return pd.DataFrame()  # Возвращаем пустой DataFrame в случае ошибки

def calculate_card_expenses(transactions):
    """Рассчитывает общую сумму расходов и кешбэк для каждой карты."""
    required_columns = ["Номер карты", "Сумма операции"]
    if not all(col in transactions.columns for col in required_columns):
        raise ValueError(f"Отсутствуют необходимые столбцы: {required_columns}")

    # Удаляем строки, где номер карты отсутствует
    transactions = transactions.dropna(subset=["Номер карты"]).copy()  # Используем .copy()

    # Извлекаем последние 4 цифры номера карты
    transactions.loc[:, "last_4_digits"] = transactions["Номер карты"].astype(str).str.extract(r'\*(\d{4})')[0]

    # Преобразуем сумму операции в числовой формат (если это еще не сделано)
    if not pd.api.types.is_numeric_dtype(transactions["Сумма операции"]):
        transactions.loc[:, "Сумма операции"] = (
            transactions["Сумма операции"]
            .str.replace(",", ".", regex=False)  # Заменяем запятую на точку
            .astype(float)  # Преобразуем в число
        )

    # Группируем по последним 4 цифрам и считаем сумму расходов
    cards = transactions.groupby("last_4_digits").agg(
        total_spent=("Сумма операции", "sum")
    ).reset_index()

    # Рассчитываем кешбэк (1 рубль на каждые 100 рублей)
    cards["cashback"] = (cards["total_spent"] // 100).round(2)

    return cards.to_dict(orient="records")

def get_top_transactions(transactions, n=5):
    """Определяет топ-N транзакций по сумме платежа."""
    required_columns = ["Сумма платежа"]
    if not all(col in transactions.columns for col in required_columns):
        raise ValueError(f"Отсутствуют необходимые столбцы: {required_columns}")

    # Преобразуем сумму платежа в числовой формат (если это еще не сделано)
    if not pd.api.types.is_numeric_dtype(transactions["Сумма платежа"]):
        transactions.loc[:, "Сумма платежа"] = (
            transactions["Сумма платежа"]
            .str.replace(",", ".", regex=False)  # Заменяем запятую на точку
            .astype(float)  # Преобразуем в число
        )

    # Сортируем по сумме платежа и выбираем топ-N
    top_transactions = transactions.sort_values("Сумма платежа", ascending=False).head(n)

    # Преобразуем даты в строки
    top_transactions.loc[:, "Дата операции"] = top_transactions["Дата операции"].dt.strftime("%Y-%m-%d %H:%M:%S")

    return top_transactions.to_dict(orient="records")
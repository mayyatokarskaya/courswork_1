import os

import pandas as pd
import pytest

from src.utils import calculate_card_expenses, filter_data_by_date, get_top_transactions, load_excel


@pytest.fixture
def sample_dataframe():
    """Фикстура для создания тестового DataFrame."""
    data = {
        "Дата операции": ["01.10.2023 12:00:00", "15.10.2023 14:00:00", "25.10.2023 18:00:00"],
        "Номер карты": ["****1234", "****5678", "****1234"],
        "Сумма операции": [1000, 500, 1500],
    }
    return pd.DataFrame(data)


@pytest.fixture
def transactions_with_payments():
    """Фикстура для DataFrame с платежами."""
    data = {
        "Сумма платежа": ["1000.50", "500.20", "1500.00", "2000.99", "50.75"],
        "Дата операции": ["2023-01-01", "2023-01-15", "2023-01-20", "2023-01-25", "2023-01-30"],
    }
    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])
    return df


@pytest.fixture
def tmp_excel_file(tmpdir):
    """Создаёт временный файл Excel."""
    data = {
        "Дата операции": ["01.10.2023 12:00:00", "15.10.2023 14:00:00"],
        "Номер карты": ["****1234", "****5678"],
        "Сумма операции": [1000, 500],
    }
    df = pd.DataFrame(data)
    file_path = tmpdir.join("operations.xlsx")
    df.to_excel(file_path, index=False)
    return file_path


# Тесты для load_excel
def test_load_excel(tmp_excel_file):
    df = load_excel(file_name=os.path.basename(tmp_excel_file))
    assert not df.empty
    # Проверяем наличие обязательных столбцов
    required_columns = {"Дата операции", "Номер карты", "Сумма операции"}
    assert required_columns.issubset(df.columns)


def test_load_excel_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_excel(file_name="nonexistent.xlsx")


# Тесты для filter_data_by_date
def test_filter_data_by_date(sample_dataframe):
    filtered = filter_data_by_date(sample_dataframe, "2023-10-15")
    assert len(filtered) == 1
    assert filtered.iloc[0]["Дата операции"] == pd.Timestamp("2023-10-01 12:00:00")


def test_filter_data_by_date_invalid_date(sample_dataframe):
    with pytest.raises(ValueError):
        filter_data_by_date(sample_dataframe, "invalid-date")


# Тесты для calculate_card_expenses
def test_calculate_card_expenses(sample_dataframe):
    result = calculate_card_expenses(sample_dataframe)
    assert len(result) == 2
    assert result[0]["total_spent"] == 2500
    assert result[0]["cashback"] == 25.00


def test_calculate_card_expenses_missing_columns():
    df = pd.DataFrame({"Номер карты": ["****1234"]})
    with pytest.raises(ValueError):
        calculate_card_expenses(df)


# Тесты для get_top_transactions
def test_get_top_transactions(transactions_with_payments):
    top_transactions = get_top_transactions(transactions_with_payments, n=3)
    assert len(top_transactions) == 3
    assert top_transactions[0]["Сумма платежа"] == 2000.99


def test_get_top_transactions_missing_columns():
    df = pd.DataFrame({"Сумма операции": [1000]})
    with pytest.raises(ValueError):
        get_top_transactions(df)


def test_get_top_transactions_invalid_sum(transactions_with_payments):
    transactions_with_payments.loc[0, "Сумма платежа"] = "invalid"
    top_transactions = get_top_transactions(transactions_with_payments)
    assert len(top_transactions) == 4  # Одна строка с некорректной суммой будет удалена

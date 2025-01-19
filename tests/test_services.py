import json
import logging

import pandas as pd
import pytest
from src.services import analyze_cashback_categories, find_transfers_to_individuals

# Фикстура для создания временного DataFrame с тестовыми данными
@pytest.fixture
def sample_transactions():
    data = {
        "Дата операции": ["01.10.2023 12:00:00", "15.08.2023 14:00:00", "10.07.2023 18:00:00"],
        "Категория": ["РЖД", "РЖД", "Такси"],
        "Кэшбэк": [50, 120, 30],
    }
    df = pd.DataFrame(data)
    return df

# Фикстура для создания временного файла Excel
@pytest.fixture
def sample_excel_file(tmpdir):
    data = {
        "Категория": ["Переводы", "Переводы", "Продукты"],
        "Описание": ["Иванов И.", "Петров П.", "Магазин 'Пятерочка'"],
    }
    df = pd.DataFrame(data)
    file_path = tmpdir.join("operations.xlsx")
    df.to_excel(file_path, index=False)
    return file_path

# Тесты для функции analyze_cashback_categories
def test_analyze_cashback_categories(sample_transactions):
    # Проверка данных из фикстуры
    logging.debug(f"Данные из фикстуры:\n{sample_transactions}")

    # Вызов функции с тестовыми данными и уменьшенным порогом
    result = analyze_cashback_categories(sample_transactions, year=2023, month=10, cashback_threshold=50)

    # Проверка результата
    logging.debug(f"Результат:\n{result}")
    result_dict = json.loads(result)
    assert "РЖД" in result_dict  # Проверка, что категория "РЖД" есть в результате
    assert result_dict["РЖД"] == 50  # Ожидаем, что сумма кэшбэка для "РЖД" будет 50 за октябрь 2023

def test_analyze_cashback_categories_no_data(sample_transactions):
    # Вызов функции с месяцем, для которого нет данных
    result = analyze_cashback_categories(sample_transactions, year=2023, month=11)

    # Проверка, что результат пустой
    result_dict = json.loads(result)
    assert result_dict == {}

def test_analyze_cashback_categories_invalid_columns():
    # Создаем DataFrame с неправильными столбцами
    data = {
        "Дата": ["01.10.2023 12:00:00"],
        "Категория": ["РЖД"],
        "Сумма": [50],
    }
    df = pd.DataFrame(data)

    # Вызов функции с неправильными столбцами
    result = analyze_cashback_categories(df, year=2023, month=10)

    # Проверка, что возвращена ошибка
    result_dict = json.loads(result)
    assert "error" in result_dict

# Тесты для функции find_transfers_to_individuals
def test_find_transfers_to_individuals(sample_excel_file):
    # Вызов функции с тестовым файлом
    result = find_transfers_to_individuals(file_path=sample_excel_file)

    # Проверка результата
    result_list = json.loads(result)
    assert len(result_list) == 2  # Два перевода физическим лицам
    assert all(item["Категория"] == "Переводы" for item in result_list)

def test_find_transfers_to_individuals_no_file():
    # Вызов функции с несуществующим файлом
    result = find_transfers_to_individuals(file_path="nonexistent_file.xlsx")

    # Проверка, что возвращена ошибка
    result_dict = json.loads(result)
    assert "error" in result_dict

def test_find_transfers_to_individuals_invalid_columns(tmpdir):
    # Создаем файл с неправильными столбцами
    data = {
        "Категория": ["Переводы"],
        "Сумма": [1000],
    }
    df = pd.DataFrame(data)
    file_path = tmpdir.join("invalid_operations.xlsx")
    df.to_excel(file_path, index=False)

    # Вызов функции с неправильными столбцами
    result = find_transfers_to_individuals(file_path=file_path)

    # Проверка, что возвращена ошибка
    result_dict = json.loads(result)
    assert "error" in result_dict
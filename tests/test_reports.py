import os
import json
import pandas as pd
from datetime import datetime, timedelta
from src.reports import save_report, spending_by_category
import pytest

# Фикстура для создания временного DataFrame с тестовыми данными
@pytest.fixture
def sample_transactions():
    data = {
        "Дата операции": ["2023-09-01 12:00:00", "2023-08-15 14:00:00", "2023-07-10 18:00:00"],
        "Категория": ["РЖД", "РЖД", "РЖД"],
        "Сумма операции": [-500, -300, -200],
    }
    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])
    return df

def test_spending_by_category(sample_transactions):
    # Вызов функции с тестовыми данными
    result = spending_by_category(sample_transactions, category="РЖД", date="2023-10-15")

    assert result["category"] == "РЖД"
    assert result["total_spent"] == 1000.0  # Сумма трат: 500 + 300 + 200
    assert result["from_date"] == "2023-07-01"  # Первый день месяца, который был три месяца назад
    assert result["to_date"] == "2023-10-15"

def test_spending_by_category_no_data(sample_transactions):
    # Вызов функции с категорией, которой нет в данных
    result = spending_by_category(sample_transactions, category="Такси", date="2023-10-15")

    # Проверка, что сумма трат равна 0
    assert result["total_spent"] == 0.0

def test_spending_by_category_invalid_date(sample_transactions):
    # Вызов функции с некорректной датой
    result = spending_by_category(sample_transactions, category="РЖД", date="invalid-date")

    # Проверка, что возвращена ошибка
    assert "error" in result

# Тесты для декоратора save_report
def test_save_report(tmpdir, sample_transactions):
    # Временная директория для сохранения отчетов
    reports_dir = tmpdir.mkdir("reports")

    # Декорируем функцию для тестирования
    @save_report(file_name="test_report.json", reports_dir=str(reports_dir))
    def dummy_function():
        return {"data": "example"}

    # Вызываем декорированную функцию
    result = dummy_function()

    # Проверяем, что файл создан
    report_file = os.path.join(reports_dir, "test_report.json")
    assert os.path.exists(report_file)

    # Проверяем содержимое файла
    with open(report_file, "r", encoding="utf-8") as f:
        file_content = json.load(f)
    assert file_content == {"data": "example"}


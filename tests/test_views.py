import json
from unittest.mock import patch
import pandas as pd
import pytest
from datetime import datetime
from src.views import generate_greeting, prepare_json_response, process_data

@pytest.mark.parametrize(
    "hour, expected_greeting",
    [
        (7, "Доброе утро"),
        (13, "Добрый день"),
        (19, "Добрый вечер"),
        (2, "Доброй ночи"),
    ],
)
def test_generate_greeting(hour, expected_greeting):
    assert generate_greeting(hour) == expected_greeting

def test_prepare_json_response():
    cards_data = [
        {"card_number": "****1234", "total_expenses": 1000, "cashback": 50},
        {"card_number": "****5678", "total_expenses": 500, "cashback": 25},
    ]
    top_transactions = [
        {"Дата операции": datetime(2023, 10, 1), "Сумма операции": 1000, "Категория": "Еда", "Описание": "Ресторан"},
        {"Дата операции": datetime(2023, 10, 15), "Сумма операции": 500, "Категория": "Магазин", "Описание": "Продукты"},
    ]
    currency_rates = {"USD": 74.5, "EUR": 82.3}
    stock_prices = {"AAPL": 175.8, "GOOGL": 2900.2}
    greeting = "Добрый день"

    expected_response = {
        "greeting": '"Добрый день"',
        "cards": cards_data,
        "top_transactions": [
            {
                "date": "01.10.2023",
                "amount": 1000,
                "category": "Еда",
                "description": "Ресторан",
            },
            {
                "date": "15.10.2023",
                "amount": 500,
                "category": "Магазин",
                "description": "Продукты",
            },
        ],
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    response = prepare_json_response(cards_data, top_transactions, currency_rates, stock_prices, greeting)
    assert json.loads(response) == expected_response


def test_process_data():
    # Подготовка данных
    data = pd.DataFrame(
        {
            "Дата операции": [datetime(2023, 10, 1), datetime(2023, 10, 15), datetime(2023, 10, 25)],
            "Номер карты": ["****1234", "****5678", "****1234"],
            "Сумма операции": [1000, 500, 1500],
            "Категория": ["Еда", "Магазин", "Развлечения"],
            "Описание": ["Ресторан", "Продукты", "Кино"],
        }
    )
    date_str = "2023-10-15"
    currencies = ["USD", "EUR"]
    stocks = ["AAPL", "GOOGL"]

    # Мокируемые данные
    mock_currency_rates = {"USD": 74.5, "EUR": 82.3}
    mock_stock_prices = {"AAPL": 175.8, "GOOGL": 2900.2}
    mock_cards_data = [{"card_number": "****1234", "total_expenses": 2500, "cashback": 125}]
    mock_top_transactions = [
        {"Дата операции": datetime(2023, 10, 1), "Сумма операции": 1000, "Категория": "Еда", "Описание": "Ресторан"},
        {"Дата операции": datetime(2023, 10, 15), "Сумма операции": 500, "Категория": "Магазин", "Описание": "Продукты"},
    ]

    # Мокируем datetime.now(), чтобы вернуть фиктивное время (например, 15:00)
    with patch("src.views.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 10, 15, 15, 0)  # Устанавливаем время 15:00
        with patch("src.views.fetch_currency_rates", return_value=mock_currency_rates):
            with patch("src.views.fetch_stock_prices", return_value=mock_stock_prices):
                with patch("src.views.filter_data_by_date", return_value=data.iloc[:2]):
                    with patch("src.views.calculate_card_expenses", return_value=mock_cards_data):
                        with patch("src.views.get_top_transactions", return_value=mock_top_transactions):
                            response = process_data(data, date_str, currencies, stocks)

    # Проверяем результат
    assert '"Добрый день"' in response
    assert "cards" in json.loads(response)
    assert "top_transactions" in json.loads(response)
    assert "currency_rates" in json.loads(response)
    assert "stock_prices" in json.loads(response)
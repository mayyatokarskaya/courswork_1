from unittest.mock import MagicMock, patch

import pytest
import requests

from src.finance_api_utils import fetch_currency_rates, fetch_stock_prices


# Тест для fetch_currency_rates с успешным запросом
@patch("requests.get")
def test_fetch_currency_rates_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "rates": {"EUR": 0.85, "GBP": 0.75, "RUB": 75.0},
    }
    mock_get.return_value = mock_response

    currencies = ["EUR", "GBP"]
    result = fetch_currency_rates(currencies)

    assert len(result) == 2
    assert result[0]["currency"] == "EUR"
    assert result[0]["rate"] == (1 / 0.85) * 75.0
    assert result[1]["currency"] == "GBP"
    assert result[1]["rate"] == (1 / 0.75) * 75.0


# Тест для fetch_currency_rates с ошибкой API
@patch("requests.get")
def test_fetch_currency_rates_api_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"success": False, "error": {"info": "Internal Server Error"}}
    mock_get.return_value = mock_response

    currencies = ["EUR", "GBP"]
    result = fetch_currency_rates(currencies)

    assert len(result) == 2
    assert result[0]["currency"] == "EUR"
    assert result[0]["rate"] is None
    assert result[1]["currency"] == "GBP"
    assert result[1]["rate"] is None


# Тест для fetch_currency_rates с отсутствием курса рубля
@patch("requests.get")
def test_fetch_currency_rates_missing_rub(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "rates": {"EUR": 0.85, "GBP": 0.75},
    }
    mock_get.return_value = mock_response

    currencies = ["EUR", "GBP"]
    with pytest.raises(ValueError, match="Курс рубля \(RUB\) не найден в ответе API."):
        fetch_currency_rates(currencies)


# Тест для fetch_stock_prices с успешным запросом
@patch("requests.get")
def test_fetch_stock_prices_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "c": 150.0,
        "o": 145.0,
        "h": 155.0,
        "l": 145.0,
    }
    mock_get.return_value = mock_response

    stocks = ["AAPL", "GOOGL"]
    result = fetch_stock_prices(stocks)

    assert len(result) == 2
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 150.0
    assert result[1]["stock"] == "GOOGL"
    assert result[1]["price"] == 150.0


# Тест для fetch_stock_prices с ошибкой API
@patch("requests.get")
def test_fetch_stock_prices_api_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"success": False, "error": {"info": "Internal Server Error"}}
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Internal Server Error")
    mock_get.return_value = mock_response

    stocks = ["AAPL", "GOOGL"]
    result = fetch_stock_prices(stocks)

    assert len(result) == 2
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] is None
    assert result[1]["stock"] == "GOOGL"
    assert result[1]["price"] is None

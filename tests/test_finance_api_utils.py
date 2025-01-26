from unittest.mock import MagicMock, patch

from src.finance_api_utils import fetch_currency_rates, fetch_stock_prices  # Импортируйте свои функции из модуля


# Тест для fetch_currency_rates с успешным запросом
@patch("requests.get")
def test_fetch_currency_rates_success(mock_get):
    # Настройка мока
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "rates": {"EUR": 0.85, "GBP": 0.75}}
    mock_get.return_value = mock_response

    currencies = ["EUR", "GBP"]
    result = fetch_currency_rates(currencies)

    # Проверка результата
    assert len(result) == 2
    assert result[0]["currency"] == "EUR"
    assert result[0]["rate"] == 0.85
    assert result[1]["currency"] == "GBP"
    assert result[1]["rate"] == 0.75


# Тест для fetch_currency_rates с ошибкой API
@patch("requests.get")
def test_fetch_currency_rates_api_error(mock_get):
    # Настройка мока
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    currencies = ["EUR", "GBP"]
    result = fetch_currency_rates(currencies)

    # Проверка, что ошибки обрабатываются
    assert len(result) == 2
    assert result[0]["currency"] == "EUR"
    assert result[0]["rate"] is None
    assert result[1]["currency"] == "GBP"
    assert result[1]["rate"] is None


# Тест для fetch_stock_prices с успешным запросом
@patch("requests.get")
def test_fetch_stock_prices_success(mock_get):
    # Настройка мока
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "c": 150.0,  # Текущая цена
        "o": 145.0,  # Цена открытия
        "h": 155.0,  # Максимум
        "l": 145.0,  # Минимум
    }
    mock_get.return_value = mock_response

    stocks = ["AAPL", "GOOGL"]
    result = fetch_stock_prices(stocks)

    # Проверка результата
    assert len(result) == 2
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 150.0
    assert result[1]["stock"] == "GOOGL"
    assert result[1]["price"] == 150.0


@patch("requests.get")
def test_fetch_stock_prices_api_error(mock_get):
    # Настройка мока
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    stocks = ["AAPL", "GOOGL"]
    result = fetch_stock_prices(stocks)

    # Проверка, что ошибки обрабатываются
    assert len(result) == 2
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] is None
    assert result[1]["stock"] == "GOOGL"
    assert result[1]["price"] is None

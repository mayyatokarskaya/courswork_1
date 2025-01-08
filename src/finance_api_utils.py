import os

import requests
from dotenv import load_dotenv

load_dotenv()


def fetch_currency_rates(currencies, base_currency="USD"):
    """
    Получение курса валют через API ExchangeRates Data API от apilayer.com.
    :param currencies: список валют, для которых нужно получить курсы (напр. ["EUR", "RUB"]).
    :param base_currency: базовая валюта (по умолчанию "USD").
    :return: список словарей с курсами валют.
    """
    # Получение API-ключа из переменных окружения
    API_KEY = os.getenv("API_KEY")
    if not API_KEY:
        raise ValueError("API_KEY не найден в переменных окружения. Добавьте его в файл .env.")

    # URL API от apilayer.com
    api_url = f"https://api.apilayer.com/exchangerates_data/latest?base={base_currency}"

    # Заголовки с API-ключом
    headers = {"apikey": API_KEY}

    results = []

    try:
        # Выполнение запроса
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Проверка успешности запроса
        data = response.json()

        # Проверка успешности ответа
        if data.get("success", False):
            rates = data.get("rates", {})
            for currency in currencies:
                rate = rates.get(currency)
                if rate:
                    results.append({"currency": currency, "rate": rate})
                else:
                    results.append({"currency": currency, "rate": None})
        else:
            print(f"Ошибка API: {data.get('error', {}).get('info', 'Неизвестная ошибка')}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка подключения к API: {e}")
        for currency in currencies:
            results.append({"currency": currency, "rate": None})

    return results


API_KEY_2 = os.getenv("FINNHUB_API_KEY")  # Убедитесь, что ваш .env содержит ключ API


def fetch_stock_prices(stocks):
    """Получение цен акций через реальный API Finnhub"""

    api_url = "https://finnhub.io/api/v1/quote"  # Реальный URL API
    results = []

    for stock in stocks:
        params = {"symbol": stock, "token": API_KEY_2}  # Символ акции  # Ваш ключ Finnhub
        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()  # Проверка на успешность запроса
            data = response.json()
            # 'c' — текущая цена, 'o' — цена открытия, 'h' — максимум, 'l' — минимум
            results.append(
                {
                    "stock": stock,
                    "price": data.get("c"),
                }
            )
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении данных для {stock}: {e}")
            results.append({"stock": stock, "price": None})

    return results

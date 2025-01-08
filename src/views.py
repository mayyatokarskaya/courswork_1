import json
from datetime import datetime
from src.utils import filter_data_by_date
from src.reports import save_excel_report
from src.services import fetch_currency_rates, fetch_stock_prices
from src.utils import calculate_card_expenses, get_top_transactions

def generate_greeting(hour: int) -> str:
    """Возвращает приветствие в зависимости от времени суток."""
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"

def prepare_json_response(cards_data, top_transactions, currency_rates, stock_prices, greeting):
    """Подготавливает JSON-ответ."""
    response = {
        "greeting": greeting,
        "cards": cards_data,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }
    return json.dumps(response, ensure_ascii=False, indent=4)


def process_data(data, date_str, currencies, stocks):
    """Обрабатывает данные, фильтрует, рассчитывает расходы и кешбэк, формирует JSON."""
    # Фильтруем данные по дате
    filtered_data = filter_data_by_date(data, date_str)

    # Получаем текущий час
    current_hour = datetime.now().hour
    greeting = generate_greeting(current_hour)

    # Анализируем данные
    cards_data = calculate_card_expenses(filtered_data)
    top_transactions = get_top_transactions(filtered_data)

    # Получаем курсы валют и цены акций
    currency_rates = fetch_currency_rates(currencies)
    stock_prices = fetch_stock_prices(stocks)

    # Формируем JSON-ответ
    response = prepare_json_response(cards_data, top_transactions, currency_rates, stock_prices, greeting)

    # Сохраняем отчет в Excel
    save_excel_report(filtered_data, f"report_{date_str}.xlsx")

    return response



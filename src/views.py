import json
import logging
import os
from datetime import datetime

import pandas as pd

import src.utils as ut
from data import PATH_DATA


def greetings() -> str:
    """
    Функция возвращает форму приветствия в зависимости от текущего времени
    :return: строка приветствия
    """
    time_now = datetime.now()

    if 5 <= time_now.hour < 11:
        greeting = "Доброе утро!"

    elif 11 <= time_now.hour < 17:
        greeting = "Добрый день!"

    elif 17 <= time_now.hour < 23:
        greeting = "Добрый вечер!"

    else:
        greeting = "Доброй ночи!"

    return greeting


def get_cards_stat(transactions: pd.DataFrame) -> list:
    """
    Функция сортирует транзакции по номерам карт и для каждой карты
    определяет сумму всех операций и сумму кэшбэка
    :param transactions: список транзакций
    :return: список формата: [{"last_digits": "номер карты",
                                "total_spent": "Сумма",
                                "cashback": "Кэшбэк"}]
    """
    filtered_transactions = ut.filter_by_state(transactions)

    filtered_transactions.loc[:, "Номер карты"] = filtered_transactions.loc[:, "Номер карты"].apply(lambda x: 'Без номера' if x is None else x)

    expense_data = filtered_transactions[filtered_transactions["Сумма операции"] < 0]

    sum_and_cur = expense_data.loc[:, ["Сумма операции", "Валюта операции"]]
    expense_data.loc[:, "Сумма операции"] = sum_and_cur.apply(
        lambda x: ut.get_transaction_sum(x) if x.iloc[1] != 'RUB' else x.iloc[0], axis=1)

    card_grouped = expense_data.groupby("Номер карты")
    card_stat = card_grouped[["Сумма операции", "Бонусы (включая кэшбэк)"]].sum()

    return [
        {
            "last_digits": number,
            "total_spent": stat["Сумма операции"],
            "cashback": stat["Бонусы (включая кэшбэк)"],
        }
        for number, stat in card_stat.iterrows()
    ]


def get_top_transactions(transactions: pd.DataFrame) -> list:
    """
    Функция возвращает список 5 самых больших операций
    :param transactions: список транзакций
    :return: список формата: [{"date": "Дата операции",
                                "amount": "Сумма операции",
                                "category": "Категория",
                                "description": "Описание"},]
    """
    filtered_transactions = ut.filter_by_state(transactions)

    expense_data = filtered_transactions[filtered_transactions["Сумма операции"] < 0]

    sum_and_cur = expense_data.loc[:, ["Сумма операции", "Валюта операции"]]
    expense_data["Сумма операции"] = sum_and_cur.apply(
        lambda x: ut.get_transaction_sum(x) if x.iloc[1] != 'RUB' else x.iloc[0], axis=1)

    expense_data["Сумма операции"] = expense_data.loc[:, "Сумма операции"].apply(lambda x: abs(x))

    sort_by_sum = expense_data.sort_values(by="Сумма операции", ascending=False)
    sort_by_sum["Дата операции"] = sort_by_sum.loc[:, "Дата операции"].astype(str)
    top_transactions = sort_by_sum.head(5)

    return [
        {
            "date": transaction["Дата операции"],
            "amount": transaction["Сумма операции"],
            "category": transaction["Категория"],
            "description": transaction["Описание"],
        }
        for _, transaction in top_transactions.iterrows()
    ]


def get_user_portfolio() -> dict:
    """
    Функция возвращает курсы валют и акция пользователя
    :return: словарь формата: {"user_currencies": [{"currency": "валюта", "rate": "курс"},],
                                "user_stocks":  [{"stock": "акция", "price": "цена"},]}
    """
    user_data = json.load(open(os.path.join(PATH_DATA, "user_settings.json")))
    rates = json.load(open(os.path.join(PATH_DATA, "currency_rates.json")))

    user_currencies = [
        {"currency": cur, "rate": 1 / rates["conversion_rates"][cur]}
        for cur in user_data["user_currencies"]
    ]
    user_stocks = [
        {"stock": stock, "price": ut.get_actual_stock_price(stock)}
        for stock in user_data["user_stocks"]
    ]

    return {"user_currencies": user_currencies, "user_stocks": user_stocks}


def make_response(date: str | datetime) -> dict[str, str | list[dict]]:
    """
    Функция формирует json-ответ для главной страницы на момент date-даты
    :param date: дата
    :return: словарь и запись в файл result.json
    """
    if type(date) is str:
        date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")

    end_date = date
    start_date = datetime(end_date.year, end_date.month, 1, 0, 0, 0)

    data = ut.read_table(os.path.join(PATH_DATA, "operations.xls"))
    filtered_transactions = ut.filter_by_date(
        data, date=[start_date, end_date], date_format="%d.%m.%Y %H:%M:%S"
    )

    greeting = greetings()
    cards = get_cards_stat(filtered_transactions)
    top_transactions = get_top_transactions(filtered_transactions)
    user_portfolio = get_user_portfolio()

    result = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": user_portfolio["user_currencies"],
        "stock_prices": user_portfolio["user_stocks"],
    }

    with open(os.path.join(PATH_DATA, "result.json"), "w", encoding="UTF-8") as f:
        json.dump(result, f, ensure_ascii=False)

    return result

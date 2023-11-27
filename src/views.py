import logging
import os
from datetime import datetime
import pandas as pd
import utils as ut
from data import PATH_DATA


def greetings() -> str:
    time_now = datetime.now()

    if 5 <= time_now.hour < 11:
        greeting = 'Доброе утро!'

    elif 11 <= time_now.hour < 17:
        greeting = 'Добрый день!'

    elif 17 <= time_now.hour < 23:
        greeting = 'Добрый вечер!'

    else:
        greeting = 'Доброй ночи!'

    return greeting


def get_cards_info(transactions: list[dict]) -> dict:
    filtered_transactions = ut.filter_by_state(transactions)

    cards = {}

    for transaction in filtered_transactions:
        try:
            number = transaction['Номер карты'][1:]
            cards.setdefault(number, {
                "spent": [],
                "cashbacks": []})
            cards[number]["spent"].append(ut.get_transaction_sum(transaction))
            cards[number]["cashbacks"].append(transaction['Кэшбэк'])

        except KeyError as e:
            logging.error(f"Ошибка: {e}", exc_info=True)

        except TypeError:
            cards.setdefault("Без номера", {"spent": [],
                                            "cashbacks": []})
            cards["Без номера"]["spent"].append(ut.get_transaction_sum(transaction))
            cards["Без номера"]["cashbacks"].append(transaction['Кэшбэк'])

    return {"cards": [{"last_digits": card,
                       "total_spent": sum(info["spent"]),
                       "cashback": sum(filter(lambda x: type(x) in (int, float), info["cashbacks"]))}
                      for card, info in cards.items()]}


def get_top_transactions(transactions: list[dict]) -> dict:
    filtered_transactions = ut.filter_by_state(transactions)

    for transaction in filtered_transactions:
        if transaction['Валюта операции'] != 'RUB':
            transaction['Сумма операции'] = ut.get_transaction_sum(transaction)

    data = pd.DataFrame(filtered_transactions)

    sort_by_sum = data.sort_values(by='Сумма операции')
    top_transactions = sort_by_sum.head(5)

    return {"top_transactions": [{"date": transaction['Дата операции'],
                                  "amount": transaction['Сумма операции'],
                                  "category": transaction['Категория'],
                                  "description": transaction['Описание']}
                                 for _, transaction in top_transactions.iterrows()]}


def get_info(date: str) -> dict[str, str | list[dict]]:
    end_date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
    start_date = datetime(end_date.year, end_date.month, 1, 0, 0, 0)

    return start_date

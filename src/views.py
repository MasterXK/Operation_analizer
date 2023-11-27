import logging
import os
from datetime import datetime
import pandas as pd
import utils as ut
from data import PATH_DATA


def filter_by_state(operations: list[dict], state: str = "OK") -> list[dict]:
    """
    Функция фильтрует список операций по статусу
    :param operations: список операций
    :param state: статус для фильтра
    :return: отфильтрованный список операций
    """
    return [operation for operation in operations if operation["Статус"] == state]


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
    sorted_transactions = filter_by_state(transactions)

    cards = {}

    for transaction in sorted_transactions:
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
    sorted_transactions = filter_by_state(transactions)
    data = pd.DataFrame(sorted_transactions)

    cards_grouped = data.groupby('Сумма платежа')
    cards_total_sum = cards_grouped['Сумма операции'].sum()
    cards_cashback_sum = cards_grouped['Кэшбэк'].sum()

    return {"cards": [{"last_digits": number[1:],
                       "total_spent": cards_total_sum[number],
                       "cashback": cards_cashback_sum[number]}
                      for number in cards_total_sum.index]}


def get_info(date: str) -> dict[str, str | list[dict]]:
    end_date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
    start_date = datetime(end_date.year, end_date.month, 1, 0, 0, 0)

    return start_date

import json
import logging
import os
import datetime as dt
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv
from typing import Iterable
from data import PATH_DATA
import numpy as np

load_dotenv()

logging.basicConfig(
    filename=os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "logs.log"
    ),
    filemode="w",
    format="%(asctime)s %(filename)s %(levelname)s: %(message)s",
    level=2,
)


def filter_by_state(transactions: pd.DataFrame, state: str = "OK") -> pd.DataFrame:
    """
    Функция фильтрует список операций по статусу
    :param transactions: список операций
    :param state: статус для фильтра
    :return: отфильтрованный список операций
    """
    return transactions[transactions["Статус"] == state]


def filter_by_date(
        transactions: pd.DataFrame,
        date_format: str = "%d.%m.%Y %H:%M:%S",
        date: str | datetime | Iterable = datetime.now().date(),
) -> pd.DataFrame:
    """
    Функция фильтрует список транзакций по дате.
    Если передана одна дата, то возвращает список транзакций в зту дату.
    Если передан итерируемый date, то возвращает транзакции в период с "первый элемент date" по "второй элемент date"
    :param transactions: список транзакций
    :param date_format: формат даты
    :param date: дата(даты)
    :return: отфильтрованный список
    """
    if transactions["Дата операции"].dtype == '<M8[ns]':
        dates = transactions["Дата операции"]
    else:
        dates = pd.to_datetime(transactions["Дата операции"])

    if not type(date) is str and isinstance(date, Iterable):
        date_iter = iter(date)
        start_date = next(date_iter)
        end_date = next(date_iter)

        if type(start_date) is datetime:
            start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            start_date = datetime.strftime(start_date, date_format)

        if type(end_date) is datetime:
            end_date = datetime.strftime(end_date, date_format)

        result = transactions[(dates >= start_date) & (dates <= end_date)]

        return result

    elif type(date) is str:
        dates = dates.dt.date
        date = datetime.strptime(date, date_format[:8]).date()
        result = transactions[dates == date]

        return result

    elif type(date) is datetime:
        dates = dates.dt.date
        date = datetime.strptime(date, date_format[:8]).date()

        result = transactions.loc[dates == date]

        return result

    else:
        logging.error(
            "Ошибка: неверный тип date. Требуется str или datetime, либо Iterable[str | datetime]"
        )
        raise TypeError("Неверный тип date. Требуется str или datetime, либо Iterable[str | datetime]")


def read_json(json_path: str | os.PathLike) -> pd.DataFrame | list:
    """
    Функция считывает содержимое json-файла
    :param json_path: абсолютный путь до json-а
    :return: содержимое json
    """
    try:
        with open(json_path, encoding="UTF-8") as json_file:
            json_content = json.load(json_file)
        logging.debug("Получены данные")

    except json.JSONDecodeError as e:
        logging.error(f"Ошибка: {e}")
        return []

    except FileNotFoundError as e:
        logging.error(f"Ошибка: {e}")
        return []

    return json_content


def read_table(file_path: str | os.PathLike) -> pd.DataFrame | None:
    """
    Функция считывает данные из таблиц .csv и .xlsx(.xls)
    :param file_path: путь до файла с таблицей
    :return: объект Python
    """
    if not os.path.exists(file_path):
        logging.error("Файл не найден")
        return None

    _, ext = os.path.splitext(file_path)

    if ext == ".csv":
        data = pd.read_csv(file_path,
                           encoding="UTF-8",
                           sep=";",
                           parse_dates=["Дата операции"],
                           date_format="%d.%m.%Y %H:%M:%S",
                           ).replace({np.nan: None})

    elif ext in [".xls", ".xlsx"]:
        data = pd.read_excel(file_path,
                             parse_dates=["Дата операции"],
                             date_format="%d.%m.%Y %H:%M:%S"
                             ).replace({np.nan: None})

    else:
        logging.error("Неизвестное расширение файла")
        raise TypeError("Неизвестное расширение файла")

    return data


def get_actual_rates() -> None:
    """
    Функция запрашивает актуальные курсы валют и сохраняет их в json-файл
    :return: None
    """
    key = os.getenv("API_EXC")

    try:
        response = requests.get(f"https://v6.exchangerate-api.com/v6/{key}/latest/RUB")
        rates_data = response.json()
        logging.debug("Данные по курсам получены.")

    except requests.exceptions.RequestException as e:
        logging.error(f"Не удалось получить данные: {e}", exc_info=True)
        return None

    with open(os.path.join(PATH_DATA, "currency_rates.json"), "w") as rates:
        json.dump(rates_data, rates)
        logging.debug(f"Данные записаны: {rates.name, rates.mode, rates.encoding}")

    return None


def get_actual_stock_price(symbol: str) -> None:
    """
    Функция получает актуальную цену акции. Сервис доступен на 25 обращений в сутки
    :param symbol: код акции
    :return: цена акции
    """
    key = os.getenv("API_AVS")

    try:
        response = requests.get(
            f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={key}"
        )

    except requests.exceptions.RequestException as e:
        logging.error(f"Не удалось получить данные: {e}", exc_info=True)
        return None

    else:
        stock_data = response.json()
        logging.debug(f"Данные акций {symbol} получены")

    try:
        rates = read_json(os.path.join(PATH_DATA, "currency_rates.json"))
        stock_price = float(stock_data["Global Quote"]["05. price"])

    except KeyError:
        result = "Сервис недоступен"

    except FileNotFoundError as e:
        logging.error(f"Нет данных по курсам валют. {e}", exc_info=True)
        raise e

    else:
        result = round(stock_price / rates["conversion_rates"]["USD"], 1)

    return result


def get_transaction_sum(transaction: pd.Series) -> float | None:
    """
    Функция возвращает сумму транзакции в рублях
    :param transaction: транзакция
    :return: сумма транзакции
    """
    currency = transaction["Валюта операции"]

    try:
        rates: dict = read_json(os.path.join(PATH_DATA, "currency_rates.json"))

    except FileNotFoundError as e:
        logging.error(f"Нет данных по курсам валют. {e}", exc_info=True)
        raise e

    if currency == "RUB":
        logging.debug("Транзакция в рублях, вывожу сумму...")
        return float(transaction["Сумма операции"])

    else:
        logging.debug(f"Транзакция в валюте {currency}, запрашиваю курс к рублю...")
        return round(
            float(transaction["Сумма операции"]) / float(rates["conversion_rates"][currency]),
            1,
        )

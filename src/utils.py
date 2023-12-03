import json
import os
from datetime import datetime
from typing import Iterable

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv

from data import PATH_DATA
from src.logger import setup_logger

load_dotenv()

logger = setup_logger()


def filter_by_state(
    transactions: pd.DataFrame, state: str = "OK"
) -> pd.DataFrame | pd.Series:
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
    date: str | datetime | Iterable = datetime.now(),
) -> pd.DataFrame | pd.Series:
    """
    Функция фильтрует список транзакций по дате.
    Если передана одна дата, то возвращает список транзакций в зту дату.
    Если передан итерируемый date, то возвращает транзакции в период с "первый элемент date" по "второй элемент date"
    :param transactions: список транзакций
    :param date_format: формат даты
    :param date: дата(даты)
    :return: отфильтрованный список
    """
    if transactions["Дата операции"].dtype == "<M8[ns]":
        dates = transactions["Дата операции"]
    else:
        dates = pd.to_datetime(transactions["Дата операции"])

    if not type(date) is str and isinstance(date, Iterable):
        date_iter = iter(date)
        start_date = next(date_iter)
        end_date = next(date_iter)

        if type(start_date) is str:
            try:
                start_date = datetime.strptime(start_date, date_format)
            except TypeError as e:
                logger.error(
                    f'Неверный формат даты. Нужно указать даты в формате: "%d%%%m%%%Y %H%%%M%%%S". {e}',
                    exc_info=True,
                )
                raise e

        if type(end_date) is str:
            try:
                start_date = datetime.strptime(start_date, date_format)
            except TypeError as e:
                logger.error(
                    f'Неверный формат даты. Нужно указать даты в формате: "%d%%%m%%%Y %H%%%M%%%S". {e}',
                    exc_info=True,
                )
                raise e

        result = transactions.loc[(dates >= start_date) & (dates <= end_date), :]

        return result

    elif type(date) is str:
        dates = dates.dt.date
        try:
            date = datetime.strptime(date, date_format[:8])
        except TypeError as e:
            logger.error(
                f'Неверный формат даты. Нужно указать дату в формате: "%d%%%m%%%Y". {e}',
                exc_info=True,
            )
            raise e

        result = transactions[dates == date.date()]

        return result

    elif type(date) is datetime:
        dates = dates.dt.date

        result = transactions.loc[dates == date.date()]

        return result

    else:
        logger.error(
            "Ошибка: неверный тип date. Требуется str или datetime, либо Iterable[str | datetime]"
        )
        raise TypeError(
            "Неверный тип date. Требуется str или datetime, либо Iterable[str | datetime]"
        )


def read_json(json_path: str | os.PathLike) -> list | dict:
    """
    Функция считывает содержимое json-файла
    :param json_path: абсолютный путь до json-а
    :return: содержимое json
    """
    try:
        with open(json_path, encoding="UTF-8") as json_file:
            json_content = json.load(json_file)
        logger.debug("Получены данные")

    except json.JSONDecodeError as e:
        logger.error(f"Ошибка: {e}")
        return []

    except FileNotFoundError as e:
        logger.error(f"Ошибка: {e}")
        return []

    return json_content


def read_table(file_path: str | os.PathLike) -> pd.DataFrame | None:
    """
    Функция считывает данные из таблиц .csv и .xlsx(.xls)
    :param file_path: путь до файла с таблицей
    :return: объект Python
    """
    if not os.path.exists(file_path):
        logger.error("Файл не найден")
        return None

    _, ext = os.path.splitext(file_path)

    if ext == ".csv":
        data = pd.read_csv(
            file_path,
            encoding="UTF-8",
            sep=";",
            parse_dates=["Дата операции"],
            date_format="%d.%m.%Y %H:%M:%S",
        ).replace({np.nan: None})

    elif ext in [".xls", ".xlsx"]:
        data = pd.read_excel(
            file_path,
            parse_dates=["Дата операции"],
            date_format="%d.%m.%Y %H:%M:%S",
        ).replace({np.nan: None})

    else:
        logger.error("Неизвестное расширение файла")
        raise TypeError("Неизвестное расширение файла")

    return data


def fet_actual_rate(symbol: str) -> float:
    """

    :param symbol:
    :return:
    """


def get_actual_rates() -> None:
    """
    Функция запрашивает актуальные курсы валют и сохраняет их в json-файл
    :return: None
    """
    key = os.getenv("API_EXC")

    if not key:
        logger.error('Ошибка: нет апи-ключа для курсов валют!')
        raise ValueError('Ошибка: нет апи-ключа для курсов валют!')

    try:
        response = requests.get(f"https://v6.exchangerate-api.com/v6/{key}/latest/RUB")
        rates_data = response.json()
        logger.debug("Данные по курсам получены.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Не удалось получить данные: {e}", exc_info=True)
        return None

    with open(os.path.join(PATH_DATA, "currency_rates.json"), "w") as rates:
        json.dump(rates_data, rates)
        logger.debug(f"Данные записаны: {rates.name, rates.mode, rates.encoding}")

    return None


def get_actual_stock_price(symbol: str) -> None | str | float:
    """
    Функция получает актуальную цену акции. Сервис доступен на 25 обращений в сутки
    :param symbol: код акции
    :return: цена акции
    """
    key = os.getenv("API_AVS")
    if not key:
        logger.error('Ошибка: нет апи-ключа для акций!')
        raise ValueError('Ошибка: нет апи-ключа для акций!')

    try:
        response = requests.get(
            f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={key}"
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"Не удалось получить данные: {e}", exc_info=True)
        return None

    else:
        stock_data = response.json()
        logger.debug(f"Данные акций {symbol} получены")

    try:
        rates = read_json(os.path.join(PATH_DATA, "currency_rates.json"))
        stock_price = float(stock_data["Global Quote"]["05. price"])

    except KeyError:
        result = "Сервис недоступен"

    except FileNotFoundError as e:
        logger.error(f"Нет данных по курсам валют. {e}", exc_info=True)
        raise e

    else:
        result = round(stock_price / float(rates["conversion_rates"]["USD"]), 2)

    return result


def get_transaction_sum(transaction: pd.Series) -> float | None:
    """
    Функция возвращает сумму транзакции в рублях
    :param transaction: транзакция
    :return: сумма транзакции
    """
    currency = transaction["Валюта операции"]

    try:
        rates = read_json(os.path.join(PATH_DATA, "currency_rates.json"))

    except FileNotFoundError as e:
        logger.error(f"Нет данных по курсам валют. {e}", exc_info=True)
        raise e

    if currency == "RUB":
        logger.debug("Транзакция в рублях, вывожу сумму...")
        return float(transaction["Сумма операции"])

    else:
        logger.debug(f"Транзакция в валюте {currency}, запрашиваю курс к рублю...")
        return round(
            float(transaction["Сумма операции"])
            / float(rates["conversion_rates"][currency]),
            2,
        )

import json
import logging
import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

from data import PATH_DATA

load_dotenv()

logging.basicConfig(
    filename=os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "logs.log"
    ),
    filemode="w",
    format="%(asctime)s %(filename)s %(levelname)s: %(message)s",
    level=2,
)


def filter_by_state(transactions: list[dict], state: str = "OK") -> list[dict]:
    """
    Функция фильтрует список операций по статусу
    :param transactions: список операций
    :param state: статус для фильтра
    :return: отфильтрованный список операций
    """
    return [
        transaction for transaction in transactions if transaction["Статус"] == state
    ]


def filter_by_date(transactions: list[dict], date_format: str,
                   start_date: str | datetime = None, end_date: str | datetime = None,
                   date: str | datetime = datetime.now().date()) -> list[dict]:
    if start_date and end_date:
        if type(start_date) is str:
            start_date = datetime.strptime(start_date, date_format)

        if type(end_date) is str:
            end_date = datetime.strptime(end_date, date_format)

        return [
            transaction for transaction in transactions
            if start_date < datetime.strptime(transaction["Дата операции"], date_format) < end_date
        ]
    else:
        if type(date) is str:
            date = datetime.strptime(date, date_format).date()
        return [
            transaction for transaction in transactions
            if datetime.strptime(transaction["Дата операции"], date_format).date() == date
        ]


def read_json(json_path: str | os.PathLike) -> list[dict] | dict:
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

    if type(json_content) in [list, dict]:
        logging.debug("Данные верны")
        return json_content

    logging.error("Ошибка: в файле не список")
    return []


def read_table(file_path: str | os.PathLike) -> list[dict] | dict | None:
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
        data = pd.read_csv(file_path, encoding="UTF-8", sep=";")

    elif ext in [".xls", ".xlsx"]:
        data = pd.read_excel(file_path)

    else:
        logging.error("Неизвестное расширение файла")
        return None

    return_data: list[dict] | dict = json.loads(
        data.to_json(orient="records", force_ascii=False)
    )

    return return_data


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
    Функция
    :param symbol:
    :return:
    """
    key = os.getenv("API_AVS")

    try:
        response = requests.get(
            f"""https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={key}"""
        )
        rates = read_json(os.path.join(PATH_DATA, "currency_rates.json"))

    except requests.exceptions.RequestException as e:
        logging.error(f"Не удалось получить данные: {e}", exc_info=True)
        return None

    else:
        stock_data = response.json()
        logging.debug(f"Данные акций {symbol} получены")

    try:
        result = round(
            float(stock_data["Global Quote"]["05. price"])
            / rates["conversion_rates"]["USD"],
            1,
        )
    except KeyError:
        result = 'Сервис недоступен'

    return result


def get_transaction_sum(transaction: dict) -> float | None:
    """
    Функция возвращает сумму транзакции в рублях
    :param transaction: транзакция
    :return: сумма транзакции
    """
    currency = transaction["Валюта операции"]

    try:
        rates: dict = read_json(os.path.join(PATH_DATA, "currency_rates.json"))

    except FileNotFoundError:
        logging.error("Файл rates_data.json не найден.")
        return None

    if currency == "RUB":
        logging.debug("Транзакция в рублях, вывожу сумму...")
        return float(transaction["Сумма операции"])

    else:
        logging.debug(f"Транзакция в валюте {currency}, запрашиваю курс к рублю...")
        return round(
            float(transaction["Сумма операции"] / rates["conversion_rates"][currency]),
            1,
        )

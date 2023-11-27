import logging
import os
import json
import pandas as pd
import requests
from dotenv import load_dotenv
from data import PATH_DATA

load_dotenv()


logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'logs.log'),
    filemode='w',
    format="%(asctime)s %(filename)s %(levelname)s: %(message)s",
    level=2)


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

    return_data: list[dict] | dict = json.loads(data.to_json(orient="records", force_ascii=False))

    return return_data


def get_actual_rate() -> None:
    key = os.getenv("API_EXC")

    try:
        response = requests.get(
            f"https://v6.exchangerate-api.com/v6/{key}/latest/RUB"
        )
        rates_data = response.json()
        logging.debug('Данные курса получены.')

    except requests.exceptions.RequestException as e:
        logging.error(f'Не удалось получить данные: {e}', exc_info=True)
        return None

    with open(os.path.join(PATH_DATA, 'rates_data.json'), 'w') as rates:
        rates.write(json.dumps(rates_data))
        logging.debug(f'Данные записаны: {rates.name, rates.mode, rates.encoding}')

    return None


def get_transaction_sum(transaction: dict) -> float | None:
    """
    Функция возвращает сумму транзакции в рублях
    :param transaction: транзакция
    :return: сумма транзакции
    """
    currency = transaction["Валюта операции"]

    try:
        data: dict = read_json(os.path.join(PATH_DATA, 'rates_data.json'))

    except FileNotFoundError:
        logging.error('Файл rates_data.json не найден.')
        return None

    if currency == "RUB":
        logging.debug('Транзакция в рублях, вывожу сумму...')
        return float(transaction["Сумма операции"])

    else:
        logging.debug(f'Транзакция в валюте {currency}, запрашиваю курс к рублю...')
        return round(
            data["conversion_rates"][currency] / float(transaction["Сумма операции"]), 1)

import pytest
import pandas as pd
import os
from datetime import datetime
from unittest.mock import patch, Mock
from src.utils import (
    get_transaction_sum,
    get_actual_stock_price,
    get_actual_rates,
    filter_by_date,
    filter_by_state,
    read_table,
    read_json,
)

from data import PATH_DATA


@pytest.fixture
def transactions() -> list[dict]:
    return [
        {"Дата операции": "17.09.2021 00:00:00",
         "Валюта операции": "RUB",
         "Сумма операции": "10"},
        {"Дата операции": "17.09.2021 00:00:00",
         "Валюта операции": "USD",
         "Сумма операции": "10"},
        {"Дата операции": "16.09.2021 00:00:00",
         "Валюта операции": "EUR",
         "Сумма операции": "10"},
        {"Дата операции": "16.09.2021 00:00:00",
         "Валюта операции": "",
         "Сумма операции": ""},
        {"Дата операции": "15.09.2021 00:00:00",
         "Валюта операции": "",
         "Сумма операции": ""},
    ]


@pytest.fixture
def date_format() -> str:
    return "%d.%m.%Y %H:%M:%S"


@pytest.fixture
def data_in() -> dict[str, str]:
    return {
        "amount": "0.0",
        "currency_code": "",
        "currency_name": "",
        "date": "",
        "description": "",
        "from": "",
        "id": "0.0",
        "state": "",
        "to": "",
    }


@pytest.fixture
def operations() -> list[dict[str, str | int]]:
    return [
        {"id": 41428829, "Статус": "OK", "date": "2019-07-03T18:35:29.512364"},
        {"id": 939719570, "Статус": "OK", "date": "2018-06-30T02:08:58.425572"},
        {"id": 594226727, "Статус": "FAILED", "date": "2018-09-12T21:27:25.241689"},
        {"id": 615064591, "Статус": "FAILED", "date": "2018-10-14T08:21:33.419441"},
    ]


@pytest.mark.parametrize(
    "date, expected_result",
    [
        (
                "17.09.2021 00:00:00",
                [
                    {"Дата операции": "17.09.2021 00:00:00",
                     "Валюта операции": "RUB",
                     "Сумма операции": "10"},
                    {"Дата операции": "17.09.2021 00:00:00",
                     "Валюта операции": "USD",
                     "Сумма операции": "10"},
                ],
        ),
        (
                datetime(day=17, month=9, year=2021),
                [
                    {"Дата операции": "17.09.2021 00:00:00",
                     "Валюта операции": "RUB",
                     "Сумма операции": "10"},
                    {"Дата операции": "17.09.2021 00:00:00",
                     "Валюта операции": "USD",
                     "Сумма операции": "10"},
                ],
        ),
        (
                ["16.09.2021 00:00:00", "17.09.2021 00:00:00"],
                [
                    {"Дата операции": "17.09.2021 00:00:00",
                     "Валюта операции": "RUB",
                     "Сумма операции": "10"},
                    {"Дата операции": "17.09.2021 00:00:00",
                     "Валюта операции": "USD",
                     "Сумма операции": "10"},
                    {"Дата операции": "16.09.2021 00:00:00",
                     "Валюта операции": "EUR",
                     "Сумма операции": "10"},
                    {"Дата операции": "16.09.2021 00:00:00",
                     "Валюта операции": "",
                     "Сумма операции": ""},
                ],
        )
    ],
)
def test_filter_by_date(date, expected_result, date_format, transactions) -> None:
    assert filter_by_date(transactions, date=date, date_format=date_format) == expected_result


def test_filter_by_date_err(date_format, transactions) -> None:
    with pytest.raises(ValueError):
        filter_by_date(transactions, date='15-09-2021', date_format=date_format)

    with pytest.raises(TypeError):
        filter_by_date(transactions, date=17.09, date_format=date_format)


def test_filter_by_state(operations: list[dict[str, str | int]]) -> None:
    assert filter_by_state(operations) == operations[:2]
    assert filter_by_state(operations, state="FAILED") == operations[2:]


@pytest.mark.parametrize(
    "json_path, expected_result",
    [
        (
                os.path.join(os.path.dirname(__file__), "test_data", "test_1.json"),
                [
                    {
                        "id": 41428829,
                        "state": "EXECUTED",
                        "date": "2019-07-03T18:35:29.512364",
                        "operationAmount": {
                            "amount": "8221.37",
                            "currency": {"name": "USD", "code": "USD"},
                        },
                        "description": "Перевод организации",
                        "from": "MasterCard 7158300734726758",
                        "to": "Счет 35383033474447895560",
                    }
                ],
        ),
        (
                os.path.join(os.path.dirname(__file__), "test_data", "test_2.json"),
                {
                    "id": 441945886,
                    "state": "EXECUTED",
                    "date": "2019-08-26T10:50:58.294041",
                    "operationAmount": {
                        "amount": "31957.58",
                        "currency": {"name": "руб.", "code": "RUB"},
                    },
                    "description": "Перевод организации",
                    "from": "Maestro 1596837868705199",
                    "to": "Счет 64686473678894779589",
                },
        ),
        (os.path.join(os.path.dirname(__file__), "test_data", "test_3.json"), []),
        (os.path.join(os.path.dirname(__file__), "test_data", "test_4.json"), []),
    ],
)
def test_read_json(json_path: str | os.PathLike, expected_result: list) -> None:
    assert read_json(json_path) == expected_result


@patch("os.path.exists")
@patch("pandas.read_csv")
@patch("pandas.read_excel")
def test_read_table(mock_read_excel: Mock,
                    mock_read_csv: Mock,
                    mock_exists: Mock,
                    data_in: dict[str, str],
                    ) -> None:
    mock_exists.return_value = True

    df = pd.DataFrame(data_in, index=[0])
    mock_read_csv.return_value = df

    assert read_table("path.csv") == [data_in]

    mock_exists.assert_called_once()
    mock_read_csv.assert_called_once()

    df = pd.DataFrame(data_in, index=[0])
    mock_read_excel.return_value = df

    assert read_table("path.xls") == [data_in]

    mock_exists.assert_called()
    mock_read_excel.assert_called_once()


@patch("builtins.open")
@patch("json.dump")
@patch("requests.get")
def test_get_actual_rates(
        mock_get: Mock, mock_dump: Mock, mock_open: Mock, data_in
) -> None:
    mock_get.return_value.json.return_value = data_in
    mock_file = mock_open.return_value.__enter__.return_value

    assert get_actual_rates() is None

    mock_get.assert_called_once()
    mock_dump.assert_called_with(data_in, mock_file)
    mock_open.assert_called_once_with(
        os.path.join(PATH_DATA, "currency_rates.json"), "w"
    )


@patch("requests.get")
@patch("os.getenv")
@patch("src.utils.read_json")
def test_get_actual_stock_price(mock_read_json: Mock, mock_get_env: Mock, mock_get: Mock, ) -> None:
    mock_get_env.return_value = 'key'
    mock_get.return_value.json.return_value = {"Global Quote": {"05. price": 30}}
    mock_read_json.return_value = {"conversion_rates": {"USD": 30}}

    assert get_actual_stock_price('test') == 1.0

    mock_get.return_value.json.return_value = {"Global Quot": {"05. price": 30}}

    assert get_actual_stock_price('test') == "Сервис недоступен"

    mock_get.assert_called_with(
        f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=test&apikey=key"
    )
    mock_get_env.assert_called()
    mock_read_json.assert_called()


@patch("src.utils.read_json")
def test_get_transaction_sum(mock_read_json: Mock, transactions) -> None:
    mock_read_json.return_value = {"conversion_rates": {"USD": 30, "RUB": 1, "EUR": 40}}

    assert get_transaction_sum(transactions[0]) == 10
    assert get_transaction_sum(transactions[1]) == 0.3

    mock_read_json.assert_called()

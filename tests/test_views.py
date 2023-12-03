import os

import pandas as pd
import pytest
from pandas.core.frame import DataFrame
from pandas import Series
from src.views import get_cards_stat, get_top_transactions
from tests import PATH_TESTS


@pytest.fixture
def transactions() -> DataFrame:
    df = pd.read_excel(
        os.path.join(PATH_TESTS, "test_data", "test_operations.xls"),
        parse_dates=["Дата операции"],
        date_format="%d.%m.%Y %H:%M:%S",
    ).replace({pd.NA: None})
    return df


def test_get_top_transactions(transactions: DataFrame) -> None:
    assert get_top_transactions(transactions) == [
        {
            "amount": 1468.0,
            "category": "Дом и ремонт",
            "date": "2021-10-28 15:56:36",
            "description": "Леруа Мерлен",
        },
        {
            "amount": 350.0,
            "category": "Развлечения",
            "date": "2021-11-24 13:00:32",
            "description": "Biletnaya Kassa 1",
        },
        {
            "amount": 300.0,
            "category": "Местный транспорт",
            "date": "2021-08-29 22:04:10",
            "description": "Метро Санкт-Петербург",
        },
        {
            "amount": 195.84,
            "category": "Каршеринг",
            "date": "2021-10-18 17:01:04",
            "description": "Ситидрайв",
        },
        {
            "amount": 160.89,
            "category": "Супермаркеты",
            "date": "2021-12-31 16:44:00",
            "description": "Колхоз",
        },
    ]


def test_get_cards_stat(transactions: DataFrame) -> None:
    assert get_cards_stat(transactions) == [
        {"cashback": 3.0, "last_digits": "*4556", "total_spent": -360.0},
        {"cashback": 45.0, "last_digits": "*7197", "total_spent": -2378.73},
    ]

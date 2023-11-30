import pytest
from unittest.mock import patch, Mock
from src.views import get_top_transactions, get_cards_stat
import pandas as pd
import os
from tests import PATH_TESTS


@pytest.fixture
def transactions() -> pd.DataFrame:
    df = pd.read_excel(os.path.join(PATH_TESTS, "test_data", "test_transactions.xls"),
                       parse_dates=["Дата операции"],
                       date_format="%d.%m.%Y %H:%M:%S"
                       ).replace({pd.NA: None})
    return df


def test_get_top_transactions(transactions) -> None:
    assert get_top_transactions(transactions) == [{'amount': 20000.0,
                                                   'category': 'Переводы',
                                                   'date': '2021-12-30 22:22:03',
                                                   'description': 'Константин Л.'},
                                                  {'amount': 800.0,
                                                   'category': 'Переводы',
                                                   'date': '2021-12-31 00:12:53',
                                                   'description': 'Константин Л.'},
                                                  {'amount': 564.0,
                                                   'category': 'Различные товары',
                                                   'date': '2021-12-31 01:23:42',
                                                   'description': 'Ozon.ru'},
                                                  {'amount': 160.89,
                                                   'category': 'Супермаркеты',
                                                   'date': '2021-12-31 16:44:00',
                                                   'description': 'Колхоз'},
                                                  {'amount': 118.12,
                                                   'category': 'Супермаркеты',
                                                   'date': '2021-12-31 16:39:04',
                                                   'description': 'Магнит'}]


def test_get_cards_stat(transactions) -> None:
    assert get_cards_stat(transactions) == [{'cashback': 5.0, 'last_digits': '*5091', 'total_spent': -571.07},
                                            {'cashback': 7.0, 'last_digits': '*7197', 'total_spent': -422.38},
                                            {'cashback': 0.0, 'last_digits': 'Без номера', 'total_spent': -20800.0}]

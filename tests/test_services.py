import os

import pandas as pd
import pytest

from src.services import invest_copilka
from tests import PATH_TESTS


@pytest.fixture
def transactions() -> pd.DataFrame:
    df = pd.read_excel(
        os.path.join(PATH_TESTS, "test_data", "test_operations.xls"),
        parse_dates=["Дата операции"],
        date_format="%d.%m.%Y %H:%M:%S",
    ).replace({pd.NA: None})
    return df


def test_invest_copilka(transactions) -> None:
    assert invest_copilka("2021-12", transactions, 50) == 55.11
    assert invest_copilka("2021-12", transactions, 10) == 15.11
    assert invest_copilka("2021-12", transactions, 100) == 105.11
    assert invest_copilka("2021-07", transactions, 100) == 0

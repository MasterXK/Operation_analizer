import pytest
import pandas as pd
import os
from tests import PATH_TESTS
from src.services import invest_copilka


@pytest.fixture
def transactions() -> pd.DataFrame:
    df = pd.read_excel(os.path.join(PATH_TESTS, "test_data", "test_transactions.xls"),
                       parse_dates=["Дата операции"],
                       date_format="%d.%m.%Y %H:%M:%S"
                       ).replace({pd.NA: None})
    return df


def test_invest_copilka(transactions) -> None:
    assert invest_copilka("2021-12", transactions, 50) == 356.55
    assert invest_copilka("2021-12", transactions, 10) == 56.55
    assert invest_copilka("2021-12", transactions, 100) == 606.55
    assert invest_copilka("2021-11", transactions, 100) == 0

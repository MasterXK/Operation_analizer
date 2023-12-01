import os
from unittest.mock import Mock, mock_open, patch

import numpy as np
import pandas as pd
import pytest

import src.utils as ut
from src.reports import report, spending_by_category
from tests import PATH_TESTS


@pytest.fixture
def transactions() -> pd.DataFrame:
    df = pd.read_excel(
        os.path.join(PATH_TESTS, "test_data", "test_operations.xls"),
        parse_dates=["Дата операции"],
        date_format="%d.%m.%Y %H:%M:%S",
    ).replace({np.nan: None})

    return df


def test_report() -> None:
    @report()
    def foo(a, b):
        return {"sum": a + b, "mul": a * b}

    with patch("builtins.open", mock_open(read_data="data")) as mock_file:
        assert foo(1, 2) == {"sum": 3, "mul": 2}

    mock_file.assert_called_once()


def test_spending_by_category(transactions) -> None:
    expected_result = transactions.loc[1]
    given_result = spending_by_category(transactions, "Фастфуд", "31.12.2021 17:00:00")
    if len(given_result) == 1:
        given_result = given_result.iloc[0]
    result = given_result.equals(expected_result)
    assert result

    expected_result = transactions.loc[5]
    given_result = spending_by_category(
        transactions, "Каршеринг", "31.10.2021 10:00:00"
    )
    if len(given_result) == 1:
        given_result = given_result.iloc[0]
    result = given_result.equals(expected_result)
    assert result

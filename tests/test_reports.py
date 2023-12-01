import pytest
import pandas as pd
import os
import numpy as np
from tests import PATH_TESTS
import src.utils as ut
from unittest.mock import patch, mock_open, Mock
from src.reports import report, spending_by_category


@pytest.fixture
def transactions() -> pd.DataFrame:
    df = pd.read_excel(os.path.join(PATH_TESTS, "test_data", "test_transactions.xls"),
                       parse_dates=["Дата операции"],
                       date_format="%d.%m.%Y %H:%M:%S"
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

    expected_result = transactions.copy()
    expected_result["Дата операции"] = expected_result["Дата операции"].astype(str)
    expected_result = expected_result.to_dict("records")

    assert spending_by_category(transactions, "Переводы", '31.12.2021 17:00:00') == expected_result[5:7]
    assert spending_by_category(transactions, "Переводы", '31.12.2021 17:00:00') == expected_result[5:7]
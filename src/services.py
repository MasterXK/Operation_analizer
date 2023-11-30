from datetime import datetime, timedelta
from typing import Any
from functools import reduce
import utils as ut
import logging
import pandas as pd


def invest_copilka(month: str, transactions: list[dict[str, Any]], limit: int) -> float:
    start_date = datetime.strptime(month, "%Y-%m")

    if start_date.month in [1, 12]:
        end_date = datetime(start_date.year, start_date.month, 31)

    else:
        end_date = datetime(start_date.year, start_date.month + 1, start_date.day) - timedelta(days=1)

    filtered_transactions = ut.filter_by_date(
        transactions, date=[start_date, end_date], date_format="%d.%m.%Y %H:%M:%S"
    )

    data = pd.DataFrame(filtered_transactions)
    expenses = data[data["Сумма операции"] < 0]

    result = reduce(lambda x, y: x + abs(y) % limit, expenses["Сумма операции"], 0)

    return round(result, 2)




from datetime import datetime, timedelta
from typing import Any
from functools import reduce
import src.utils as ut
import logging
import pandas as pd


def invest_copilka(month: str, transactions: pd.DataFrame, limit: int) -> float:
    start_date = datetime.strptime(month, "%Y-%m")

    if start_date.month == 12:
        end_date = datetime(year=start_date.year + 1, month=1, day=1)

    else:
        end_date = datetime(start_date.year, start_date.month + 1, start_date.day)

    filtered_transactions = ut.filter_by_date(
        transactions, date=[start_date, end_date], date_format="%d.%m.%Y %H:%M:%S"
    )

    expenses = filtered_transactions[filtered_transactions["Сумма операции"] < 0]

    result = reduce(lambda x, y: x + limit - abs(y) % limit, expenses["Сумма операции"].tolist(), 0)

    return round(result, 2)




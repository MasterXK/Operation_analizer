import utils as ut
import pandas as pd
import json
import logging
import os
from functools import wraps
from typing import Callable, Optional
from data import PATH_DATA
from datetime import datetime


def report(file_name: str = 'report.json') -> Callable:
    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)

            with open(os.path.join(PATH_DATA, func.__name__ + file_name), "w", encoding="UTF-8") as f:
                json.dump(result, f, ensure_ascii=False)

            return result

        return inner

    return wrapper


@report()
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = datetime.now()) -> pd.DataFrame:
    if type(date) is str:
        end_date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
    else:
        end_date = date

    if end_date.month <= 3:
        start_date = datetime(year=end_date.year - 1, month=12 - 3 + end_date.month, day=end_date.day)

    else:
        start_date = datetime(year=end_date.year, month=end_date.month - 3, day=end_date.day)

    filtered_transactions = ut.filter_by_date(transactions, date=[start_date, end_date])

    expense_data = filtered_transactions[filtered_transactions["Сумма операции"] < 0]

    sum_and_cur = expense_data.loc[:, ["Сумма операции", "Валюта операции"]]
    expense_data.loc[:, "Сумма операции"] = sum_and_cur.apply(
        lambda x: ut.get_transaction_sum(x) if x.iloc[1] != 'RUB' else x.iloc[0], axis=1)

    category_expenses = expense_data[expense_data["Категория"] == category]
    category_expenses["Дата операции"] = category_expenses["Дата операции"].astype(str)

    return category_expenses.to_dict("records")

import json
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Optional

import pandas as pd

import src.utils as ut
from data import PATH_DATA


def report(file_name: str = "report") -> Callable:
    """
    Декоратор для записи результата работы функции в файл
    :param file_name: имя файла, по-умолчанию 'report.json'
    :return: результат работы декорируемой функции
    """
    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)
            output = result.copy()

            if type(result) is pd.DataFrame:
                result["Дата операции"] = result["Дата операции"].astype(str)

                with pd.ExcelWriter(os.path.join(PATH_DATA, func.__name__ + file_name + '.xlsx')) as writer:
                    result.to_excel(writer)

                return output

            with open(os.path.join(PATH_DATA, func.__name__ + file_name + '.json'), "w", encoding="UTF-8", ) as f:
                json.dump(result, f, ensure_ascii=False)

            return output

        return inner

    return wrapper


@report()
def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> pd.DataFrame | list[str]:
    """
    Функция возвращает фрейм трат по категории category за последние 3 месяца
    :param transactions: список транзакций
    :param category: категория
    :param date: дата для начала отсчета
    :return: фрейм
    """
    if date:
        end_date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")

    else:
        end_date = datetime.now()

    if end_date.month <= 3:
        start_date = datetime(
            year=end_date.year - 1, month=12 - 3 + end_date.month, day=end_date.day
        )

    else:
        start_date = datetime(
            year=end_date.year, month=end_date.month - 2, day=1
        ) - timedelta(days=1)

    filtered_transactions = ut.filter_by_date(transactions, date=[start_date, end_date])

    expense_data = filtered_transactions[filtered_transactions["Сумма операции"] < 0]

    sum_and_cur = expense_data[["Сумма операции", "Валюта операции"]]
    expense_data.loc[:, "Сумма операции"] = sum_and_cur.apply(
        lambda x: ut.get_transaction_sum(x) if x.iloc[1] != "RUB" else x.iloc[0], axis=1
    )

    category_expenses = expense_data.loc[(expense_data["Категория"] == category)]

    if category_expenses.empty:
        return ["Такой категории нет"]

    return category_expenses

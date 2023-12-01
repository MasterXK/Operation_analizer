from datetime import datetime
from functools import reduce

import pandas as pd

import src.utils as ut
from src.logger import setup_logger

logger = setup_logger()


def invest_copilka(month: str, transactions: pd.DataFrame, limit: int) -> float:
    try:
        start_date = datetime.strptime(month, "%Y-%m")

    except TypeError as e:
        logger.error(
            f'Неверный формат даты. Нужно указать месяц в формате: "%Y-%m". {e}',
            exc_info=True,
        )
        raise e

    if start_date.month == 12:
        end_date = datetime(year=start_date.year + 1, month=1, day=1)

    else:
        end_date = datetime(year=start_date.year, month=start_date.month + 1, day=1)

    filtered_transactions = ut.filter_by_date(
        transactions, date=[start_date, end_date], date_format="%d.%m.%Y %H:%M:%S"
    )

    expenses = filtered_transactions[filtered_transactions["Сумма операции"] < 0]

    result = reduce(
        lambda x, y: x + limit - abs(y) % limit, expenses["Сумма операции"].tolist(), 0
    )

    return round(result, 2)

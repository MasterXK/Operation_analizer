import os
from pprint import pprint
from data import PATH_DATA
from tests import PATH_TESTS
from datetime import datetime
import pandas as pd

import utils as ut
import views as vw
import services as svs
import reports as reps


def main():
    ut.get_actual_rates()
    transactions = ut.read_table(os.path.join(PATH_TESTS, "test_data", "test_transactions.xls"))
    vw.make_response('30.12.2021 22:22:03', transactions)
    svs.invest_copilka()
    pprint(reps.spending_by_category(transactions, "Переводы",  '31.12.2021 17:00:00'))


if __name__ == "__main__":
    main()

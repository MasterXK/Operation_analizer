import os
from pprint import pprint

import src.reports as reps
import src.services as svs
import src.utils as ut
import src.views as vw
from data import PATH_DATA


def main():
    ut.get_actual_rates()
    transactions = ut.read_table(os.path.join(PATH_DATA, "operations.xls"))

    vw.make_response("30.12.2021 22:22:03", transactions)
    print("=" * 100)
    print(
        "С инвесткопилкой за сентябрь 2021-го Вы бы отложили: ",
        svs.invest_copilka("2021-09", transactions, 50),
        " рублей",
    )
    print("=" * 100)
    print('Траты в категории "Переводы": ')
    pprint(reps.spending_by_category(transactions, "Переводы", "31.12.2021 17:00:00"))


if __name__ == "__main__":
    main()

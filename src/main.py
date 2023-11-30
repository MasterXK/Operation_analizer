import os
from pprint import pprint
from data import PATH_DATA
from datetime import datetime
import pandas as pd

import utils as ut
import views as vw
import services as svs
import reports as reps

pd.set_option("display.min_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_colwidth", None)


def main():
    ut.get_actual_rates()
    # pprint(vw.make_response('30.12.2021 22:22:03'), sort_dicts=False)
    df = ut.read_table(os.path.join(PATH_DATA, "operations.xls"))
    # pprint(df['Дата операции'])
    print(reps.spending_by_category(df, 'Такси', '26.12.2021 22:09:56'))


if __name__ == "__main__":
    main()

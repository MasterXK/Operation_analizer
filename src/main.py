import os
from pprint import pprint
from data import PATH_DATA
from datetime import datetime
import pandas as pd

import utils as ut
import views as vw
import services as svs

pd.set_option("display.min_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_colwidth", None)


def main():
    ut.get_actual_rates()
    # vw.make_response('30.12.2021 22:22:03')
    data = ut.read_table(os.path.join(PATH_DATA, "operations.xls"))
    print(svs.invest_copilka('2021-12', data, 50))


if __name__ == "__main__":
    main()

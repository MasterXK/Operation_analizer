import os
from pprint import pprint
from data import PATH_DATA
from datetime import datetime
import pandas as pd

import utils as ut
import views as vw

pd.set_option("display.min_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_colwidth", None)


def main():
    ut.get_actual_rates()
    # vw.make_response('30.12.2021 22:22:03')
    data = ut.read_table(os.path.join(PATH_DATA, "operations.xls"))
    pprint(vw.get_cards_stat(data))


if __name__ == "__main__":
    main()

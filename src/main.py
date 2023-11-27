from pprint import pprint

import utils as ut
import views as vw
import pandas as pd
import os


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

ut.get_actual_rate()

data = ut.read_table(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'operations.xls'))

# cards = vw.get_cards_info(data)
top_transactions = vw.get_top_transactions(data)
pprint(top_transactions)

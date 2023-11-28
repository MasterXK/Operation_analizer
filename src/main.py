import os
from pprint import pprint
from data import PATH_DATA
import pandas as pd

import utils as ut
import views as vw

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def main():
    ut.get_actual_rates()
    # vw.get_info('30.12.2021 22:22:03')
    data = pd.DataFrame(ut.read_table(os.path.join(PATH_DATA, "operations.xls")))

    test = data.loc[:, ['Сумма операции', 'Валюта операции']]
    test_ = test.apply(lambda x: x.iloc[0] * 2 if x.iloc[1] == 'RUB' else 0, axis=1)
    print(test_)
    test['Сумма операции'] = test_
    print(test)
    # print(data.apply(lambda x: x ** 2, axis='Сумма операции'))


if __name__ == '__main__':
    main()

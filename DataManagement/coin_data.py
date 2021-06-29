import sys
sys.path.append('./')
from constants import STRING_KEY_NUM_MINUTE_DICT

class CoinData():

    def __init__(self, df, coin_sybmol, kline_size_string):

        self.df = df
        self.coin_sybmol = coin_sybmol
        self.kline_size_string = kline_size_string
        self.num_minutes = STRING_KEY_NUM_MINUTE_DICT[self.kline_size_string]

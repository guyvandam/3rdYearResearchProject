import sys
sys.path.append('./')

from onstants import STRING_KEY_NUM_MINUTE_DICT
from DataManagement.data_manager import DataManager

class DataFrame():

    def __init__(self, coin_sybmol, kline_size_string):

        self.df = DataManager().get_historical_data_DataFrame(coin_sybmol, kline_size_string)
        self.coin_sybmol = coin_sybmol
        self.kline_size_string = kline_size_string
        self.num_minutes = STRING_KEY_NUM_MINUTE_DICT[self.kline_size_string]
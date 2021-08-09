from DataManagement.data_manager import DataManager
from DataManagement.coin_data import CoinData
from TransferEntropy.transfer_entropy import TransferEntropy
from constants import ATR_ABNORMALITY_COLUMN
# libs
import pandas as pd
import numpy as np

# plotting
import seaborn as sn
import matplotlib.pyplot as plt
# plt.rcParams["figure.figsize"] = (70,30)

coin_symbol_list = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "LTCUSDT"]
feature = "close_pct"
kline_size = "1h"
main_coin_symbol = "BTCUSDT"
transfer_entropy_lookback = 24


class TransferEntropyResearch():

    def __init__(self):

        self.data_manager = DataManager()
        self.transfer_entropy = TransferEntropy(lookback=transfer_entropy_lookback)

        self.main_1h_df = self.data_manager.get_historical_data_CoinData(main_coin_symbol, kline_size="1h").df
        self.coin_data_list = [self.data_manager.get_historical_data_CoinData(coin_symbol, kline_size="1m") for coin_symbol in coin_symbol_list]

    def join_dataframes(self):
        df = pd.DataFrame(index=self.coin_data_list[0].df.index)

        for coin_data in self.coin_data_list:
            df = df.join(coin_data.df[feature], how="outer", rsuffix=f"_{coin_data.coin_symbol}", on="timestamp")

        df.rename(columns={"close_pct":f"close_pct_{self.coin_data_list[0].coin_symbol}"}, inplace=True)    
        df.dropna(inplace=True)
        df.drop(columns=["timestamp"])
        df.set_index("timestamp", inplace=True)
        return df



if __name__ == '__main__':
    print()

    te_research = TransferEntropyResearch()
    print(te_research.join_dataframes())

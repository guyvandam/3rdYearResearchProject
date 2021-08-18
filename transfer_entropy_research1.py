from DataManagement.data_manager import DataManager
from DataManagement.coin_data import CoinData
from TransferEntropy.transfer_entropy import get_transfer_entropy
from constants import ATR_ABNORMALITY_COLUMN
from tqdm import tqdm
# libs
import pandas as pd
import numpy as np

# plotting
import seaborn as sn
import matplotlib.pyplot as plt
# plt.rcParams["figure.figsize"] = (70,30)

coin_symbol_list = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "LTCUSDT"]
feature = "close"
kline_size = "1h"
main_coin_symbol = "BTCUSDT"
transfer_entropy_lookback = 2
suptitle_fontsize = 40
font_scale = 3
candle_size = "1d"
num_samples = 1440 # 60*24


data_manager = DataManager()
        # self.transfer_entropy = TransferEntropy(lookback=transfer_entropy_lookback, window_size=num_samples)

main_1d_df = data_manager.get_historical_data_CoinData(main_coin_symbol, kline_size="1d").df
coin_data_list = [data_manager.get_historical_data_CoinData(coin_symbol, kline_size="1m") for coin_symbol in coin_symbol_list]
# main_1h_df = data_manager.get_historical_data_CoinData(main_coin_symbol, kline_size="1h").df
main_abnormal_timestamp_list = main_1d_df[main_1d_df[ATR_ABNORMALITY_COLUMN] == 1].index



def join_dataframes(coin_data_list, shift):
    df = pd.DataFrame(index=coin_data_list[0].df.index)

    for coin_data in coin_data_list:
        df = df.join(coin_data.df.shift(shift)[feature], how="outer", rsuffix=f"_{coin_data.coin_symbol}", on="timestamp")

    df.rename(columns={"close_pct":f"close_pct_{coin_data_list[0].coin_symbol}"}, inplace=True)    
    df.dropna(method="backfill", inplace=True)
    df.drop(columns=["timestamp"])
    df.set_index("timestamp", inplace=True)
    return df



raw_df = join_dataframes(coin_data_list=coin_data_list, shift=0)

 
df = raw_df["2021-01-01":].resample("5min").median()

 
print(df.describe())


def replaceZeroes(data):
  min_nonzero = np.min(data[np.nonzero(data)])
  data[data == 0] = min_nonzero
  return data

df = data_manager.add_noise_to_df(df, mu = 0, sigma = 10)
df.fillna(value=df.median(), inplace=True)
# df.fillna(method="backfill", inplace=True)
print(np.sum(df.duplicated(subset=["close"])))
quit()
num_cols = len(df.columns)
n = len(df)
L = 1
result = np.ones(shape=(num_cols, num_cols))
for i, coli in enumerate(df.columns):
    for j, colj in enumerate(df.columns): 
        arr1 = df[coli].to_numpy()
        arr2 = df[colj].to_numpy()
        
        # print(np.where(arr1 is None))
        # print(np.where(arr2 is None))
        # print(max(arr1))
        # print(max(arr2))
        
        entropy_value = get_transfer_entropy(np.array([arr1[0:n-L], arr1[1:n]]), np.array([arr2[0:n-1], arr2[1:n]]))
        print(entropy_value)
        result[i, j] = entropy_value

 
result = pd.DataFrame(data=result, columns=df.columns, index=df.columns)
sn.heatmap(result, annot=True)
    
 




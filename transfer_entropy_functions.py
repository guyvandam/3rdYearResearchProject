from TransferEntropy.transfer_entropy import TransferEntropy
from DataManagement.data_manager import DataManager
import numpy as np
import pandas as pd
lookback = 1
def get_transfer_entropy_matrix(df):
    
    num_cols = df.shape[1]
    result = np.ones(shape=(num_cols, num_cols))
    temp_result = np.ones(shape=(num_cols, num_cols))
    
    skipping_counter = 0
    resampled_list = np.array(df.resample("1h"))

    for i, (timestamp, temp_df) in enumerate(resampled_list):
        
        if temp_df.empty or i < lookback:
            skipping_counter += 1
            continue
        
        
        candle_series = resampled_list[i-lookback:i, :]
        candle_series = [t_df for _, t_df in candle_series]
        print(candle_series)
        
        if i == 2:
            return

def join_dataframes(coin_data_list, shift):
    df = pd.DataFrame(index=coin_data_list[0].df.index)

    for coin_data in coin_data_list:
        df = df.join(coin_data.df.shift(shift)[feature], how="outer", rsuffix=f"_{coin_data.coin_symbol}", on="timestamp")

    df.rename(columns={"close_pct":f"close_pct_{coin_data_list[0].coin_symbol}"}, inplace=True)    
    df.dropna(inplace=True)
    df.drop(columns=["timestamp"])
    df.set_index("timestamp", inplace=True)
    return df 

if __name__ == "__main__":
    coin_symbol_list = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "LTCUSDT"]
    feature = "close_pct"
    kline_size = "1h"
    main_coin_symbol = "BTCUSDT"
    transfer_entropy_lookback = 1


    data_manager = DataManager()
    transfer_entropy = TransferEntropy(lookback=transfer_entropy_lookback)

    coin_data_list = [data_manager.get_historical_data_CoinData(coin_symbol, kline_size="1m") for coin_symbol in coin_symbol_list]
    one_min_df = join_dataframes(coin_data_list=coin_data_list, shift=0)

    get_transfer_entropy_matrix(one_min_df)

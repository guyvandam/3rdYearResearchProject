from DataManagement.data_manager import DataManager
from TransferEntropy.transfer_entropy import get_transfer_entropy

import numpy as np
import pandas as pd
from tqdm import tqdm
from constants import HLOC

data_manager = DataManager()


def get_transfer_entropy_matrix(df,L):
    num_cols = len(df.columns)
    n = len(df)
    result = np.ones(shape=(num_cols, num_cols))
    for i, coli in tqdm(enumerate(df.columns)):
        for j, colj in enumerate(df.columns): 
            list_i, list_j = [], []
            arr_i = df[coli].to_numpy()
            arr_j = df[colj].to_numpy()

            # create windows.
            for l in range(L+1):
                list_i.append(arr_i[l:n-L+l])
                list_j.append(arr_j[l:n-L+l])
            
            entropy_value = get_transfer_entropy(np.array(list_i), np.array(list_j))
            if entropy_value is np.nan:
                quit()
            
            result[i, j] = entropy_value
            
    return pd.DataFrame(data=result, columns=df.columns, index=df.columns)


def add_hloc(input_df):
    input_df[HLOC] = input_df[["high", "low", "open", "close"]].mean(axis=1)

def join_dataframes(coin_data_list, feature):
    df = pd.DataFrame(index=coin_data_list[0].df.index)

    for coin_data in coin_data_list:
        if feature == HLOC:
            add_hloc(coin_data.df)
        
        df = df.join(coin_data.df[feature], how="outer", rsuffix=f"_{coin_data.coin_symbol}", on="timestamp")
    
    df.rename(columns={feature:f"{feature}_{coin_data_list[0].coin_symbol}"}, inplace=True)    
    df.dropna(how="any", inplace=True)
    df.drop(columns=["timestamp"])
    df.set_index("timestamp", inplace=True)
    return df

def get_transfer_entropy_matrix_wrapper(raw_df, L=3):
    df = raw_df["2021-01-01":].resample("5min").median()
    data_manager.add_noise_to_df(df, sigma_value=10)
    df.dropna(how="any", inplace=True)
    return get_transfer_entropy_matrix(df, L=L)

if __name__ == "__main__":
    coin_symbol_list = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "LTCUSDT"]
    kline_size = "1h"
    main_coin_symbol = "BTCUSDT"
    transfer_entropy_lookback = 1



    coin_data_list = [data_manager.get_historical_data_CoinData(coin_symbol, kline_size="1m") for coin_symbol in coin_symbol_list]
    one_min_df = join_dataframes(coin_data_list=coin_data_list, shift=0)

    get_transfer_entropy_matrix(one_min_df)

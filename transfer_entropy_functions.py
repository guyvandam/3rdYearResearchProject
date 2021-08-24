from DataManagement.data_manager import DataManager
from TransferEntropy.transfer_entropy import get_transfer_entropy
from TransferEntropy.transfer_entropy import EEC

import numpy as np
import pandas as pd
from tqdm import tqdm
from constants import HLOC

data_manager = DataManager()


def get_transfer_entropy_matrix(df,L, is_divide_by_joint_entropy):
    num_cols = len(df.columns)
    n = len(df)
    result = np.ones(shape=(num_cols, num_cols))
    for i, coli in tqdm(enumerate(df.columns)):
        for j, colj in enumerate(df.columns): 
            joint_entropy = 1
            list_i, list_j = [], []
            arr_i = df[coli].to_numpy()
            arr_j = df[colj].to_numpy()

            # create windows.
            for l in range(L+1):
                list_i.append(arr_i[l:n-L+l])
                list_j.append(arr_j[l:n-L+l])
            
            if is_divide_by_joint_entropy:
                joint_entropy = EEC(np.array([arr_i, arr_j]).T)

            entropy_value = get_transfer_entropy(np.array(list_i), np.array(list_j))
            if entropy_value is np.nan or joint_entropy is np.nan:
                quit()
            
            result[i, j] = entropy_value/joint_entropy
            
    return pd.DataFrame(data=result, columns=df.columns, index=df.columns)


def add_hloc(input_df):
    input_df[HLOC] = input_df[["high", "low", "open", "close"]].mean(axis=1)

def join_dataframes(coin_data_list, feature):
    df = pd.DataFrame(index=coin_data_list[0].df.index)
    
    for coin_data in coin_data_list:
        if feature == HLOC:
            add_hloc(coin_data.df)
        
        df = df.join(other=coin_data.df[feature], how="inner", rsuffix=f"_{coin_data.coin_symbol}", on="timestamp")
    
    df.rename(columns={feature:f"{feature}_{coin_data_list[0].coin_symbol}"}, inplace=True)
    df.reset_index(inplace=True)
    df.drop_duplicates(subset="timestamp", keep="first", inplace=True)
    df.set_index(keys=["timestamp"], inplace=True)
    df.fillna(method='ffill', inplace=True)
    # df.dropna(how="any", inplace=True)

    return df

def get_dataframe_different_assets(asset_symbol_list, candle_size, feature = "hloc"):
    coin_data_list = [data_manager.get_historical_data_CoinData(asset_symbol, kline_size=candle_size) for asset_symbol in asset_symbol_list]
    return join_dataframes(coin_data_list, feature)

def get_transfer_entropy_matrix_wrapper(raw_df, L=3, is_divide_by_joint_entropy=True):
    df = raw_df["2021-01-01":].resample("5min").median()
    data_manager.add_noise_to_df(df, sigma_value=10)
    df.dropna(how="any", inplace=True)
    return get_transfer_entropy_matrix(df, L=L, is_divide_by_joint_entropy=is_divide_by_joint_entropy)



if __name__ == "__main__":
    coin_symbol_list = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "LTCUSDT"]
    kline_size = "1h"
    main_coin_symbol = "BTCUSDT"
    transfer_entropy_lookback = 1



    coin_data_list = [data_manager.get_historical_data_CoinData(coin_symbol, kline_size="1m") for coin_symbol in coin_symbol_list]
    one_min_df = join_dataframes(coin_data_list=coin_data_list, shift=0)

    get_transfer_entropy_matrix(one_min_df)

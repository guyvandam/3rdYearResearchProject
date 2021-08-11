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

class TransferEntropyResearch():

    def __init__(self):

        self.data_manager = DataManager()
        # self.transfer_entropy = TransferEntropy(lookback=transfer_entropy_lookback, window_size=num_samples)

        self.main_1d_df = self.data_manager.get_historical_data_CoinData(main_coin_symbol, kline_size="1d").df
        self.coin_data_list = [self.data_manager.get_historical_data_CoinData(coin_symbol, kline_size="1m") for coin_symbol in coin_symbol_list]
        # main_1h_df = data_manager.get_historical_data_CoinData(main_coin_symbol, kline_size="1h").df
        self.main_abnormal_timestamp_list = self.main_1d_df[self.main_1d_df[ATR_ABNORMALITY_COLUMN] == 1].index
        self.df = None
        # rows = 500
        # cols = 4
        # a = np.array([[i]*rows for i in range(cols)])
        # self.df = pd.DataFrame(columns=[f"col{i}" for i in range(cols)], data=a.T)
        # self.df["timestamp"] = pd.date_range("2018-01-01", periods=rows, freq="h")
        # self.df.set_index(keys=["timestamp"], inplace=True)
        
    def join_dataframes(self):
        self.df = pd.DataFrame(index=self.coin_data_list[0].df.index)

        for coin_data in self.coin_data_list:
            self.df = self.df.join(coin_data.df[feature], how="outer", rsuffix=f"_{coin_data.coin_symbol}", on="timestamp")

        self.df.rename(columns={"close_pct":f"close_pct_{self.coin_data_list[0].coin_symbol}"}, inplace=True)    
        self.df.dropna(inplace=True)
        self.df.drop(columns=["timestamp"])
        self.df.set_index("timestamp", inplace=True)

        # self.df = self.df["2020-01-01":]
        # return df

    # def get_transfer_entropy_matrix_list_old(self):
    #     num_cols = self.df.shape[1]

    #     alltime_correlation_matrix_list, abnormal_correlation_matrix_list = [],[]
    #     resampled_list = np.array(self.df.resample("1d"))
        
    #     resampled_array = np.array([temp_df.to_numpy() for _, temp_df in resampled_list])
        
    #     r = 0
    #     for iter, timestamp in enumerate([timestamp for timestamp, _ in resampled_list]):
    #         temp_correl_matrix = np.empty(shape=(num_cols, num_cols))
            
    #         if iter < transfer_entropy_lookback:
    #             continue

    #         for i in range(num_cols):
    #             for j in range(num_cols):
    #                 arr1 = np.array([arr[:, i] for arr in resampled_array[iter-transfer_entropy_lookback:iter]])
    #                 arr2 = np.array([arr[:, j] for arr in resampled_array[iter-transfer_entropy_lookback:iter]])
    #                 transfer_entropy = get_transfer_entropy(arr1, arr2)
    #                 temp_correl_matrix[i,j] = 0 if np.isnan(transfer_entropy) else transfer_entropy
    #                 # temp_correl_matrix[i,j] = i+j
            
    #         # print(temp_correl_matrix)
    #         if timestamp in self.main_abnormal_timestamp_list:
    #             abnormal_correlation_matrix_list.append(temp_correl_matrix)

    #         alltime_correlation_matrix_list.append(temp_correl_matrix)
            
    #         if r == 3:
    #             break
    #         r+=1

    #     return np.array(alltime_correlation_matrix_list), np.array(abnormal_correlation_matrix_list)

    def get_transfer_entropy_matrix_list(self):
        num_cols = self.df.shape[1]

        alltime_correlation_matrix_list, abnormal_correlation_matrix_list = [],[]
        resampled_list = self.df.resample(candle_size) # 1d
        
        # normalize dfs by subtracting the mean.
        resampled_list = [(timestamp, df.sub(df.mean(axis=0))) for timestamp, df in resampled_list]

        for iter, (timestamp, _) in tqdm(enumerate(resampled_list)):
            temp_correl_matrix = np.empty(shape=(num_cols, num_cols))
            
            if iter < transfer_entropy_lookback:
                continue
            
            for i, coli in enumerate(self.df.columns):
                for j, colj in enumerate(self.df.columns):
                    is_skip = False
                    arr1 = [temp_df[coli].to_numpy() for _, temp_df in resampled_list[iter-transfer_entropy_lookback:iter]]
                    arr2 = [temp_df[colj].to_numpy() for _, temp_df in resampled_list[iter-transfer_entropy_lookback:iter]]
                    
                    for a1, a2 in zip(arr1, arr2):
                        if len(a1) != num_samples or len(a2) != num_samples:
                            is_skip = True
                            break

                    
                    transfer_entropy_value = 0 if is_skip else get_transfer_entropy(np.flip(arr1, axis=0), np.flip(arr2, axis=0))
                    temp_correl_matrix[i,j] = 0 if np.isnan(transfer_entropy_value) else transfer_entropy_value

            # if np.all(temp_correl_matrix == 0):
            #     continue

            if timestamp in self.main_abnormal_timestamp_list:
                abnormal_correlation_matrix_list.append(temp_correl_matrix)

            alltime_correlation_matrix_list.append(temp_correl_matrix)
            

        return np.array(alltime_correlation_matrix_list), np.array(abnormal_correlation_matrix_list)
                
    def plot_heatmap_on_axes(self, data, title, axes):
        fig_size = 10
        sn.set(rc={"figure.figsize":tuple([fig_size]*2)}, font_scale = font_scale)
        
        size = 4
        mean_corr_df = pd.DataFrame(index=coin_symbol_list[:size], columns=coin_symbol_list[:size], data=data)
        sn.heatmap(mean_corr_df, annot=True, ax=axes).set(title=title)

    def plot_heatmap(self):
        fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(70,20))
        fig_title = f"Settings - feature:{feature} | time-frame:{kline_size} | main-coin:{main_coin_symbol}"
        fig.suptitle(fig_title, fontsize = suptitle_fontsize)
        
        alltime_correlation_matrix_list, abnormal_correlation_matrix_list = self.get_transfer_entropy_matrix_list()

        alltime_correl_mean = alltime_correlation_matrix_list.mean(axis=0)
        abnormal_correl_mean = abnormal_correlation_matrix_list.mean(axis=0)
        correl_method = "Transfer_Entropy"
        
        title_data_dict = {
            f"alltime Mean of {candle_size} {correl_method}": alltime_correl_mean, 
            f"abnormal Mean of {candle_size} {correl_method}": abnormal_correl_mean, 
            "abnormal minus alltime": abnormal_correl_mean-alltime_correl_mean}
        
        for i, (title, data) in enumerate(title_data_dict.items()):
            self.plot_heatmap_on_axes(data=data, title=title, axes=axes[i])
        
        fig.tight_layout()
        filename = f"{correl_method}_research_plot_normalized_by_mean_subtraction.jpg"
        fig.savefig(filename)
    

if __name__ == '__main__':
    te_research = TransferEntropyResearch()
    te_research.join_dataframes()
    # te_research.get_transfer_entropy_matrix_list()
    te_research.plot_heatmap()
    print("finished")

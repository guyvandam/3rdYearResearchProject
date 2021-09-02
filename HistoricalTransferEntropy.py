from TransferEntropy.TransferEntropy import TransferEntropy
from TransferEntropy.transfer_entropy import get_transfer_entropy
from TransferEntropy.estimate_entropy_using_copulas import estimateEntropyUsingCopulas as EEC
from transfer_entropy_functions import get_dataframe_different_assets
import numpy as np
import pandas as pd
import time
from datetime import datetime
import os


class HistoricalTransferEntropy:
    def __init__(self, assets):
        self.assets = assets
        self.one_m_df = get_dataframe_different_assets(assets, '1m')
        self.one_m_df.columns = assets
        self.invalid_timestamps = None

    def add_noise(self, multiplier):
        for asset in self.one_m_df:
            min_val = min(self.one_m_df[asset])
            noise = np.random.normal(0, min_val * multiplier, len(self.one_m_df[asset]))
            self.one_m_df[asset] += noise

    def find_invalid_timestamps(self, resampled_list: list, valid_length: int):
        timestamps_to_skip = []
        for timestamp, df in resampled_list:
            if len(df) != valid_length:
                timestamps_to_skip.append(timestamp)
        self.invalid_timestamps = timestamps_to_skip

    def is_valid_window(self, window_timestamps: list):
        for timestamp in window_timestamps:
            if timestamp in self.invalid_timestamps:
                return False
        return True

    def create_windows(self, resampled_list: list, window_size: int):
        windows = []
        invalid_windows_counter = 0
        list_length = len(resampled_list)
        for i in range(len(resampled_list)):
            start_index = i
            end_index = i + window_size
            if end_index > list_length:
                break
            window_dfs = [tup[1] for tup in resampled_list[start_index: end_index]]
            window_timestamps = [tup[0] for tup in resampled_list[start_index: end_index]]
            if self.is_valid_window(window_timestamps):
                windows.append(window_dfs)
            else:
                invalid_windows_counter += 1
        return windows, invalid_windows_counter

    def compute_historical_TE(self, window_size: int, sub_tf: str, minutes_on_sub_tf: int,
                              max_subs=None, calc_joint_entropy=False, save_results=True):

        start_time = time.time()
        dir_name = datetime.now().strftime("%m-%d-%Y__%H:%M:%S")

        # prepare the windows:
        sub_tf_tuples = list(self.one_m_df.resample(sub_tf))
        if max_subs:
            sub_tf_tuples = sub_tf_tuples[-max_subs:]  # for short tests
        self.find_invalid_timestamps(resampled_list=sub_tf_tuples, valid_length=minutes_on_sub_tf)
        windows, invalid_windows_count = self.create_windows(resampled_list=sub_tf_tuples, window_size=window_size)

        # TEST
        windows = windows[:]

        # data validation log:
        total_subs = len(sub_tf_tuples)
        invalid_subs = len(self.invalid_timestamps)
        valid_subs = total_subs - invalid_subs
        subs_used = round((valid_subs / total_subs) * 100, 2)

        total_windows = len(windows) + invalid_windows_count
        invalid_windows = invalid_windows_count
        valid_windows = len(windows)
        windows_used = round((valid_windows / total_windows) * 100, 2)

        print("")
        print(f"parameters: window={window_size}, sub_tf={sub_tf}, minutes_on_sub_tf={minutes_on_sub_tf}")
        print("")
        print(f"Total subs: {total_subs}")
        print(f"Valid subs: {valid_subs}")
        print(f"Invalid subs: {invalid_subs}")
        print("")
        print(f"Subs used: {subs_used}%")
        print("")
        print(f"Total windows: {total_windows}")
        print(f"Valid windows: {valid_windows}")
        print(f"Invalid windows: {invalid_windows}")
        print("")
        print(f"Windows used: {windows_used}%")
        print("")

        # initialize the TE_dictionary (Transfer Entropy) and JE_dictionary (Joint Entropy) with empty lists.
        TE_dict = {}
        JE_dict = {}
        for asset1 in self.assets:
            TE_dict[asset1] = {}
            JE_dict[asset1] = {}
            for asset2 in self.assets:
                TE_dict[asset1][asset2] = []
                JE_dict[asset1][asset2] = []

        # compute mean historical TE.
        for asset1 in self.assets:
            for asset2 in self.assets:
                for i, window in enumerate(windows):

                    print(f"\rComputing historical TE of {asset1},{asset2}"
                          f" - {round((i / len(windows)) * 100, 2)}%", end='')

                    asset1_iids = np.array([df[asset1].values for df in window])
                    asset2_iids = np.array([df[asset2].values for df in window])

                    timestamp = window[0].index[0]
                    TE = get_transfer_entropy(asset1_iids, asset2_iids)

                    if calc_joint_entropy:
                        joint_entropy = EEC(np.vstack([asset1_iids, asset2_iids]).T)
                        JE_dict[asset1][asset2].append((timestamp, joint_entropy))

                    TE_dict[asset1][asset2].append((timestamp, TE))

                print(f"\rComputing historical TE of {asset1},{asset2}"
                      f" - 100%")

        TE_columns = []
        for asset1 in TE_dict:
            for asset2 in TE_dict[asset1]:
                TE_columns.append(f'{asset1}_{asset2}')

        first_key = list(TE_dict.keys())[0]
        first_keys_fist_key = list(TE_dict[first_key].keys())[0]
        TE_index = [tup[0] for tup in TE_dict[first_key][first_keys_fist_key]]

        TE_data = {}
        for asset1 in TE_dict:
            for asset2 in TE_dict[asset1]:
                TE_data[f'{asset1}_{asset2}'] = [tup[1] for tup in TE_dict[asset1][asset2]]

        TE_df = pd.DataFrame(data=TE_data, columns=TE_columns, index=TE_index)

        JE_data = {}
        for asset1 in JE_dict:
            for asset2 in JE_dict[asset1]:
                JE_data[f'{asset1}_{asset2}'] = [tup[1] for tup in JE_dict[asset1][asset2]]

        JE_df = pd.DataFrame(data=JE_data, columns=TE_columns, index=TE_index)

        if save_results:
            dir_name = 'results/' + dir_name
            os.makedirs(dir_name, exist_ok=True)
            info_path = dir_name + '/info.csv'
            with open(info_path, 'w+') as info_file:
                info_file.write(f'assets: {str(self.assets)[1:-1]}\n')
                info_file.write(f'window_size: {window_size}\n')
                info_file.write(f'sub_tf: {sub_tf}\n')
                info_file.write(f'minutes_on_sub_tf: {minutes_on_sub_tf}\n')
                info_file.write(f'max_subs: {max_subs}\n')
            TE_path = dir_name + '/TransferEntropy.csv'
            JE_path = dir_name + '/JointEntropy.csv'
            TE_df.to_csv(TE_path)
            JE_df.to_csv(JE_path)

        print()
        print(f"--- finished in {round(time.time() - start_time, 1)} seconds ---")
        print()

        return TE_df, JE_df

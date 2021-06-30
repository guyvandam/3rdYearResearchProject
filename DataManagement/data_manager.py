import sys
import os.path
import os
sys.path.append('./')

from DataManagement.pre_processing_functions import PreProcess
from DataManagement.file_path_manager import FilePathManager
from DataManagement.research_coin_symbols import research_ocin_symbol_list
from DataManagement.coin_data import CoinData
from dateutil import parser
from binance.client import Client
import pandas as pd
import math

from datetime import datetime

from constants import (STRING_KEY_NUM_MINUTE_DICT, TIMESTAMP_COLUMN,
                       TIMESTAMP_FORMAT, CLOSE_COLUMN, VOLUME_COLUMN)


class DataManager:

    def __init__(self):
        self.file_path_manager_obj = FilePathManager()
        self.pre_process_obj = PreProcess()

        API_KEY = '7NHvWCOeZH6vYvTsjel1GJ3ab1bf59lYXVAsyLa8KEH6nIQG7zD7546s2HF86Gdq'
        API_SECRET = 'dU3sV6hd5rfkwT8iNtK2wFjAyJMvAfl9ywGQcZyIXAvI5CGz19z90wmKrNs1EgJX'

        self.binance_client = Client(api_key=API_KEY, api_secret=API_SECRET)

    def _initialize_binance_client(self):
        API_KEY = '7NHvWCOeZH6vYvTsjel1GJ3ab1bf59lYXVAsyLa8KEH6nIQG7zD7546s2HF86Gdq'
        API_SECRET = 'dU3sV6hd5rfkwT8iNtK2wFjAyJMvAfl9ywGQcZyIXAvI5CGz19z90wmKrNs1EgJX'

        self.binance_client = Client(api_key=API_KEY, api_secret=API_SECRET)

    def get_historical_data_CoinData(self, symbol: str, kline_size: str) -> CoinData:
        return CoinData(self.get_historical_data_DataFrame(symbol, kline_size), symbol, kline_size_string=kline_size)

    def get_historical_data_DataFrame(self, symbol, kline_size) -> pd.DataFrame:
        symbol = symbol.upper()
        self.__is_possible_kline_size(kline_size)
        file_path = self.file_path_manager_obj.get_historical_data_csv_file_path(
            symbol, kline_size)

        if os.path.isfile(file_path):
            df = pd.read_csv(file_path)
        else:
            self.__get_all_binance(symbol, kline_size)

        self.__set_timestamp_index(df)

        return df

    def __set_timestamp_index(self, df):
        df[TIMESTAMP_COLUMN] = pd.to_datetime(
            df[TIMESTAMP_COLUMN], format=TIMESTAMP_FORMAT)
        df.set_index(TIMESTAMP_COLUMN, inplace=True)

    def __minutes_of_new_data(self, symbol, kline_size, data, source):
        if len(data) > 0:
            old = parser.parse(data["timestamp"].iloc[-1])
        elif source == "binance":
            old = datetime.strptime('1 Jan 2017', '%d %b %Y')
        if source == "binance":
            new = pd.to_datetime(self.binance_client.get_klines(
                symbol=symbol, interval=kline_size)[-1][0], unit='ms')
        return old, new

    def __get_all_binance(self, symbol, kline_size, save=False):
        file_path = self.file_path_manager_obj.get_historical_data_csv_file_path(
            symbol, kline_size)
        if os.path.isfile(file_path):
            data_df = pd.read_csv(file_path)
        else:
            data_df = pd.DataFrame()
        oldest_point, newest_point = self.__minutes_of_new_data(
            symbol, kline_size, data_df, source="binance")
        delta_min = (newest_point - oldest_point).total_seconds()/60
        available_data = math.ceil(
            delta_min/STRING_KEY_NUM_MINUTE_DICT[kline_size])

        if oldest_point == datetime.strptime('1 Jan 2017', '%d %b %Y'):
            print('Downloading all available %s data for %s. Be patient..!' %
                  (kline_size, symbol))
        else:
            print('Downloading %d minutes of new data available for %s, i.e. %d instances of %s data.' % (
                delta_min, symbol, available_data, kline_size))

        klines = self.binance_client.get_historical_klines(symbol, kline_size, oldest_point.strftime(
            "%d %b %Y %H:%M:%S"), newest_point.strftime("%d %b %Y %H:%M:%S"))
        data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close',
                            'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')

        if len(data_df) > 0:
            temp_df = pd.DataFrame(data)
            data_df = data_df.append(temp_df)
        else:
            data_df = data

        self.__set_timestamp_index(data_df)

        # delete uneccery columns
        columns_to_delete = ['close_time', 'quote_av',
                             'trades', 'tb_base_av', 'tb_quote_av', 'ignore']
        for column in data_df.columns:
            if column in columns_to_delete:
                del data_df[column]
            else:
                data_df[column] = pd.to_numeric(
                    data_df[column], errors='coerce')

        # add columns
        self.pre_process_obj.add_precent_change_column(data_df, CLOSE_COLUMN)
        self.pre_process_obj.add_precent_change_column(data_df, VOLUME_COLUMN)
        self.pre_process_obj.add_atr_column(data_df)
        self.pre_process_obj.add_atr_abnormality_column(data_df)
        if kline_size in ['1h', '4h', '1d']:
            one_minute_df = self.get_historical_data_DataFrame(symbol, '1m')
            self.pre_process_obj.add_high_to_low_precent_change_column(
                data_df, kline_size, one_minute_df)

        if save:
            data_df.to_csv(file_path)
        print('All caught up..!')
        return data_df

    def download_historical_data(self, time_frames: list = None, coin_pairs: list = None):
        time_frames = ["1m", "5m", "15m", "1h", "4h",
                       "1d"] if time_frames is None else time_frames
        
        coin_pairs = ["BTCUSDT", "ETHUSDT", "LTCUSDT",
                      "ADAUSDT"] if coin_pairs is None else coin_pairs
        for time_frame in time_frames:
            for coin_pair in coin_pairs:
                print("coin_pair: %s" % coin_pair)
                self.__get_all_binance(coin_pair, time_frame, save=True)

    def __is_possible_kline_size(self, kline_size):
        if not kline_size in STRING_KEY_NUM_MINUTE_DICT.keys():
            print('not a possible kline size')
            exit()


if __name__ == "__main__":

    dm = DataManager()
    dm.download_historical_data(time_frames=["1d", "4h", "1h"], coin_pairs=research_ocin_symbol_list)

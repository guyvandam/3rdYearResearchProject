import os

class FilePathManager():

    def __init__(self):
        pass
    
    def __get_historical_data_folder_path(self):
        cwd = os.getcwd()
        return os.path.join(cwd, 'HistoricalData')

    def get_historical_data_csv_file_path(self, symbol, kline_size):
        historical_data_folder = self.__get_historical_data_folder_path()
        sybmol_folder_name = symbol
        csv_file_name = f"{symbol}-{kline_size}-data.csv"

        sybmol_folder_location = os.path.join(historical_data_folder, sybmol_folder_name)
        csv_file_path = os.path.join(sybmol_folder_location, csv_file_name)
        return csv_file_path
    
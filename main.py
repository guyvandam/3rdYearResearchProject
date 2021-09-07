from historical_transfer_entropy import HistoricalTransferEntropy
from DataManagement.data_manager import DataManager
from results_analysis import ResultsAnalysis
class Main():
    
    def __init__(self, asset_list):
        self.asset_list = asset_list
        self.data_manager = DataManager()

        self.results_analysis_object = None

        self.historical_transfer_entropy_object = HistoricalTransferEntropy(self.asset_list)
        self.execution_timestamp = ""
        

    def download_historical_data(self):
        self.data_manager.download_historical_data(time_frames=['1m'], coin_pairs=self.asset_list)
    
    def compute_hte(self):
        self.historical_transfer_entropy_object.add_noise(0.01)
        TE_df, JE_df, self.execution_timestamp = self.historical_transfer_entropy_object.compute_historical_TE(7, '1d', 1440, calc_joint_entropy=True, max_subs=None)

    def create_results_analysis(self):
        if self.results_analysis_object is None:
            self.results_analysis_object = ResultsAnalysis(self.execution_timestamp)

        if self.execution_timestamp == "":
            self.compute_hte()
        
        self.results_analysis_object.create_histogram_plot()
        self.results_analysis_object.create_mean_and_std_heatmaps()
        self.results_analysis_object.create_time_dependent_plot()
    
    def main(self):
        self.download_historical_data()
        self.compute_hte()
        self.create_results_analysis()


if __name__ == "__main__":
    m = Main(asset_list=["BTCUSDT", "ETHUSDT", "ADAUSDT"])
    m.main()
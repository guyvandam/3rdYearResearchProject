import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
def read_csv_wrapper(filepath) -> pd.DataFrame:
    df = pd.read_csv(filepath, index_col = 0)
    df.set_index(pd.to_datetime(df.index), inplace = True)
    return df


class ResultsAnalysis:


    def __init__(self,run_timestamp):
        self.run_timestamp = run_timestamp
        
        self.div_df = None
        self.te_df = None
        self.je_df = None
        self.info_df = None

        self.asset_list = []
        self.asset_string = ""
        self.ncols = 0
        self.folder = f"results/{self.run_timestamp}"

    def initialize(self):
        self.je_df = read_csv_wrapper(f"{self.folder}/JointEntropy.csv")
        self.te_df = read_csv_wrapper(f"{self.folder}/TransferEntropy.csv")
        self.info_df = pd.read_csv(f"{self.folder}/info.csv")
        self.div_df = self.te_df/self.je_df

        self.asset_list = [col.strip('assets:').strip(" '") for col in self.info_df.columns]
        self.asset_string = '_'.join(self.asset_list)
        self.ncols = len(self.asset_list)

    # there might be a problem with saving it in this function. maybe it will return the plot and we'll save it at the notebook.
    def create_histogram_plot(self, df = None):
        if df is None:
            df = self.div_df
        
        fig, axes = plt.subplots(ncols=self.ncols, nrows=self.ncols, figsize=(20,20));

        i, j = 0,0
        for col in df.columns:
            if j == self.ncols:
                j = 0
                i+=1
            df[col].hist(ax=axes[i,j], density=True);
            if j == 0:
                axes[i,j].set_ylabel(self.asset_list[i])
            if i == 0:
                axes[i,j].set_xlabel(self.asset_list[j])    
                axes[i,j].xaxis.set_label_position('top') 
                
            j+=1
        filename = self.folder + "/histogram.jpg"
        plt.savefig(filename)
        plt.close()

    def __get_matrix_df(self, series):

        i, j = 0,0
        matrix = np.empty(shape=(self.ncols, self.ncols))
        for col in series.index:
            if j == self.ncols:
                j = 0
                i+=1
            
            matrix[i, j] = series[col]
                
            j+=1

        return pd.DataFrame(data=matrix, index=self.asset_list, columns=self.asset_list)

    def __create_heatmap(self, df, function_to_run):
        if df is None:
            df = self.div_df
        if function_to_run == "mean":
            matrix_df = self.__get_matrix_df(df.mean())
        elif function_to_run == "std":
            matrix_df = self.__get_matrix_df(df.std())
        sns.heatmap(matrix_df, annot=True).set_label(f"all_time_{function_to_run}");
        filename = self.folder + f"/{function_to_run}_heatmap.jpg"
        plt.savefig(filename)
        plt.close()

    def create_mean_heatmap(self, df=None):
        self.__create_heatmap(df, "mean")

    def create_std_heatmap(self, df=None):
        self.__create_heatmap(df, "std")


if __name__ == "__main__":

    ra = ResultsAnalysis("09-02-2021__14:51:26")
    ra.initialize()

    ra.create_histogram_plot()
    ra.create_mean_heatmap()
    ra.create_std_heatmap()


    
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


    def create_time_dependent_plot(self, df=None):
        description = ""
        if df is None:
            df = self.div_df
            description = "Transfer Entropy Divided by Joint Entropy"
        
        df.rename(columns=lambda x: x.replace("_", "->"), inplace=True)
        columns_to_plot = [col for col in df.columns if len(set(col.split("->"))) > 1]
        title = f"{description} Between Pairs as Time Dependent Variables" 
       
        plt.rc('legend',**{'fontsize':15})

        df[columns_to_plot].plot(layout=(self.ncols, self.ncols-1), subplots=True, figsize=(15,12), fontsize=15)
        fig = plt.gcf()
        fig.suptitle(title, fontsize=16)

        filename = self.folder + "/time_dependent_variables.jpg"
        plt.savefig(filename)
        plt.close()

    def create_histogram_plot(self, df = None):
        description = ""
        if df is None:
            df = self.div_df
            description = "Transfer Entropy Divided by Joint Entropy"

        
        fig, axes = plt.subplots(ncols=self.ncols, nrows=self.ncols, figsize=(18,18));
        
        
        i, j = 0,0
        for col in df.columns:
            if j == self.ncols:
                j = 0
                i+=1
            df[col].hist(ax=axes[i,j], density=True);
            axes[i,j].tick_params(axis='both', labelsize=15)
            if j == 0:
                axes[i,j].set_ylabel(self.asset_list[i], fontsize = 15)
            if i == 0:
                axes[i,j].set_xlabel(self.asset_list[j], fontsize = 15)    
                axes[i,j].xaxis.set_label_position('top') 
                
            j+=1
        filename = self.folder + "/histogram.jpg"
        title = f"Histograms of {description} Between Pairs" 
        
        fig.suptitle(title, fontsize=25)

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
        description = ""
        if df is None:
            df = self.div_df
            description = "Transfer Entropy Divided by Joint Entropy"

        if function_to_run == "Mean":
            matrix_df = self.__get_matrix_df(df.mean())
        elif function_to_run == "Std":
            matrix_df = self.__get_matrix_df(df.std())
        
        title = f"All Time {function_to_run} of {description}" 
        sns.heatmap(matrix_df, annot=True).set_title(title);
        filename = self.folder + f"/{function_to_run}_heatmap.jpg"
        plt.savefig(filename)
        plt.close()

    def create_mean_heatmap(self, df=None):
        self.__create_heatmap(df, "Mean")

    def create_std_heatmap(self, df=None):
        self.__create_heatmap(df, "Std")

    # def create_time_dependent_plot(self, df=None):
    #     self.div_df.plot(subplots=True, figsize= (15,30))
    #     filename = self.folder + f"/time_dependent.jpg"
    #     plt.savefig(filename)
    #     plt.close()

if __name__ == "__main__":

    ra = ResultsAnalysis("09-02-2021__14:51:26")
    ra.initialize()

    # ra.create_histogram_plot()
    # ra.create_mean_heatmap()
    # ra.create_std_heatmap()
    # ra.create_time_dependent_plot()
    ra.create_time_dependent_plot()

    
from DataManagement.data_manager import DataManager
from DataManagement.coin_data import CoinData
from TransferEntropy.transfer_entropy import TransferEntropy
from constants import ATR_ABNORMALITY_COLUMN
# libs
import pandas as pd
import numpy as np

# plotting
import seaborn as sn
import matplotlib.pyplot as plt
# plt.rcParams["figure.figsize"] = (70,30)

# mutual information
from sklearn.feature_selection import mutual_info_classif

np.random.seed(seed=1)

num_of_points = 15000
shift = 1

x_mu = 0
x_sigma = 1
x_size = (num_of_points,)
x = np.random.normal(loc=x_mu, scale=x_sigma, size=x_size)

ksi_mu = 0
ksi_sigma = 0.1
ksi_size = (num_of_points,)
ksi = np.random.normal(loc=ksi_mu, scale=ksi_sigma, size=ksi_size)


num_of_points -= shift

y = x[:num_of_points] + ksi[:num_of_points]
x = x[shift:]
ksi = ksi[shift:]

# x = np.array(range(1,21))
# y = np.array(range(40,61))

transfer_entropy = TransferEntropy(window_size=10000, lookback=2)

transpose = True
prints = False

xy_te = transfer_entropy.get_transfer_entropy(x,y,transpose=transpose,prints=prints)
print('TransferEntropy(x,y) =', xy_te, end='\n\n')


yx_te = transfer_entropy.get_transfer_entropy(y,x,transpose=transpose,prints=prints)
print('TransferEntropy(y,x) =', yx_te)

# print()
# print('x:/n',x)
# print()
# print('y:/n',y)
# print()

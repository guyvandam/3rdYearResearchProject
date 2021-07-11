import numpy as np
from TransferEntropy.estimate_entropy_using_copulas import estimateEntropyUsingCopulas as EEC

class TransferEntropy:


    def __init__(self, dim: int = 1, lookback: int = 0):
        self.dim = dim
        self.lookback = lookback
    
    def get_correct_array(self,arr: np.array):
        if len(arr.shape) == 1:
            return arr.reshape((len(arr), 1))
        return arr

    def get_transfer_entropy(self, arr1: np.ndarray, arr2: np.ndarray):
    
        # assume the start of each list is the earliest point,  
        # and the end of each list is the latest point.

        arr1 = arr1[-self.lookback:]
        arr2 = arr2[-self.lookback:]

        arr1, arr2 = self.get_correct_array(arr1), self.get_correct_array(arr2)


        # if self.dim == 1:
        #     arr1 = arr1.reshape(len(arr1), 1)
        #     arr2 = arr2.reshape(len(arr2), 1)

        TE = EEC(xs=arr2) - \
            EEC(xs=arr2[:-1]) - \
            EEC(xs=np.concatenate((arr2, arr1[:-1]))) + \
            EEC(xs=np.concatenate((arr2[:-1], arr1[:-1])))

        return TE

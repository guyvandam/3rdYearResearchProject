import numpy as np
from TransferEntropy.estimate_entropy_using_copulas import estimateEntropyUsingCopulas as EEC

class TransferEntropy:


    def __init__(self, dim: int = 1, lookback: int = 0):
        self.dim = dim
        self.lookback = lookback
    

    def transfer_entropy(self, arr1: np.ndarray, arr2: np.ndarray, dim: int = 1, lookback: int = 0):
    
        # assume the start of each list is the earliest point,  
        # and the end of each list is the latest point.

        arr1 = arr1[-lookback:]
        arr2 = arr2[-lookback:]


        if dim == 1:
            arr1 = arr1.reshape(len(arr1), 1)
            arr2 = arr2.reshape(len(arr2), 1)

        TE = EEC(xs=arr2) - \
            EEC(xs=arr2[:-1]) - \
            EEC(xs=np.concatenate((arr2, arr1[:-1]))) + \
            EEC(xs=np.concatenate((arr2[:-1], arr1[:-1])))

        return TE

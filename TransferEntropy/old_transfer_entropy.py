import numpy as np
from TransferEntropy.estimate_entropy_using_copulas import estimateEntropyUsingCopulas as EEC
class TransferEntropy:

    def __init__(self, lookback :int , window_size: int):
        self.lookback = lookback
        self.window_size = window_size
    
    def get_correct_array(self,arr: np.array):
        if len(arr.shape) == 1:
            return arr.reshape((len(arr), 1))
        return arr
    def get_iid(self, arr: np.array, current_lookback: int):
        return arr[len(arr)-self.window_size-current_lookback:len(arr)-current_lookback]
    
    def get_iid_matrix(self, arr: np.array):
        iid_matrix = np.array([self.get_iid(arr, 0)])
        for current_lookback in range(1, self.lookback):
            iid_matrix = np.vstack((iid_matrix, self.get_iid(arr, current_lookback)))
        return iid_matrix
            
        
    def get_transfer_entropy(self, arr1: np.ndarray, arr2: np.ndarray,
                            transpose: bool = False, prints: bool = False):
    
        # assume the start of each list is the earliest point,  
        # and the end of each list is the latest point.
        # arr1, arr2 = self.get_correct_array(arr1), self.get_correct_array(arr2)
        arr1_iids = self.get_iid_matrix(arr1)
        arr2_iids = self.get_iid_matrix(arr2)
        if prints:
            print('arr1_iids:\n', arr1_iids, end='\n\n')
            print('arr2_iids:\n', arr2_iids, end='\n\n')
        e1_xs = arr2_iids
        e2_xs = arr2_iids[1:]
        e3_xs = np.vstack((arr2_iids,arr1_iids[1:]))
        e4_xs = np.vstack((arr2_iids[1:],arr1_iids[1:]))
        if transpose:
            e1_xs = e1_xs.T
            e2_xs = e2_xs.T
            e3_xs = e3_xs.T
            e4_xs = e4_xs.T
        if prints:
            print('e1_xs\n',e1_xs, end='\n\n')
            print('e2_xs\n',e2_xs, end='\n\n')
            print('e3_xs\n',e3_xs, end='\n\n')
            print('e4_xs\n',e4_xs)
            print()
        e1 = EEC(xs=e1_xs)
        e2 = EEC(xs=e2_xs)
        e3 = EEC(xs=e3_xs)
        e4 = EEC(xs=e4_xs)
        # if prints:
        print()
        print('e1:', e1)
        print('e2:', e2)
        print('e3:', e3)
        print('e4:', e4)
        print()
        TE = e1-e2-e3+e4
        print('TE: ',TE)
        print()
        return TE
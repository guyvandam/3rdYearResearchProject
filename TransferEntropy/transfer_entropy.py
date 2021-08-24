import numpy as np
from TransferEntropy.estimate_entropy_using_copulas import estimateEntropyUsingCopulas as EEC
        
def get_transfer_entropy(arr1_iids: np.ndarray, arr2_iids: np.ndarray, prints: bool = False):

    # assume the start of each list is the earliest iid,  
    # and the end of each list is the latest iid.

    if prints:
        print('arr1_iids:\n', arr1_iids, end='\n\n')
        print('arr2_iids:\n', arr2_iids, end='\n\n')

    e1_xs = arr2_iids
    e2_xs = arr2_iids[1:]
    e3_xs = np.vstack((arr2_iids, arr1_iids[1:]))
    e4_xs = np.vstack((arr2_iids[1:], arr1_iids[1:]))

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

    if prints:
        print()
        print('e1:', e1)
        print('e2:', e2)
        print('e3:', e3)
        print('e4:', e4)
        print()
    

    TE = e1-e2-e3+e4
    
    if prints:
        print('TE: ',TE)
        print()

    return TE
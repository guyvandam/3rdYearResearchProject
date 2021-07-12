import pandas as pd
import numpy as np
def get_correl_matrix(arr : np.ndarray, method: function, column_name_list: list = None) -> pd.DataFrame:
    shape = arr.shape
    cols = shape[1]
    result = np.ones(shape=(cols,cols))

    for i in range(shape[0]):
        for j in range(shape[1]):
            if i == j:
                continue
            print(arr[i])
            result[i,j] = method(arr[i], arr[j])

    return result




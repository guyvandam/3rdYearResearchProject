import numpy as np


class TransferEntropy:
    def __init__(self, TE_dict: dict):
        self.TE_dict = TE_dict

    def __repr__(self):
        s = ''
        s += 'TransferEntropy between '
        s += ','.join(self.TE_dict.keys())
        s += ':\n'
        for x in self.TE_dict:
            for y in self.TE_dict:
                s += f'TE({x},{y}) = {self.TE_dict[x][y]}\n'
        return s

    def __str__(self):
        return self.__repr__()

    def get_matrix(self):
        rows = []
        for x in self.TE_dict:
            row = []
            for y in self.TE_dict:
                row.append(self.TE_dict[x][y])
            row_array = np.array(row)
            rows.append(row_array)
        matrix = np.array(rows)
        return matrix

    def get_dict(self):
        return self.TE_dict


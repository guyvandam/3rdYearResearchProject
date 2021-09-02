from HistoricalTransferEntropy import HistoricalTransferEntropy
from constants import *


def main():
    assets = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
    HTE = HistoricalTransferEntropy(assets)
    HTE.add_noise(0.01)
    TE_df, JE_df = HTE.compute_historical_TE(7, '1d', 1440, calc_joint_entropy=True, max_subs=None)


if __name__ == "__main__":
    main()

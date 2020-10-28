import os

import numpy as np
import pandas as pd

from pprint import pprint

import matplotlib.pyplot as plt


def get_shifted_MS(ms_df, CAS_ID):
    """
    Gets the shifted ms data given a cas id.
    """

    ms_spec_data = np.array(ms_df[CAS_ID])

    # Get the maximum array index
    max_index = np.argmax(ms_spec_data)
    index_offset_tups = list((abs(max_index - index), value)
                             for index, value in enumerate(ms_spec_data))
    index_offset_tups = sorted(index_offset_tups)

    _, shifted_MS = zip(*index_offset_tups)

    shifted_MS = np.array(shifted_MS)

    return shifted_MS


def shift_all_MS():
    ms_data_path = os.path.join('data', 'MASS_SPEC_DF.csv')
    ms_df = pd.read_csv(ms_data_path)

    shifted_dict = {}

    # Get all the CAS IDs
    CAS_IDS = ms_df.columns[1:2]

    for cas_id in CAS_IDS:

        original_ms = ms_df[cas_id]
        shifted_MS = get_shifted_MS(ms_df, cas_id)

        shifted_dict[cas_id] = shifted_MS

        """
        plt.plot(range(len(original_ms)), original_ms, color='blue')
        plt.xticks(rotation=-20)
        plt.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=False,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=False)  # labels along the bottom edge are off
        plt.xlabel("m/z")
        plt.ylabel("Relative Intensity")
        plt.title('MS spec for ' + cas_id)
        plt.show()

        plt.plot(range(len(shifted_MS)), shifted_MS, color='blue')
        plt.xticks(rotation=-20)
        plt.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=False,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=False)  # labels along the bottom edge are off
        plt.xlabel("m/z")
        plt.ylabel("Relative Intensity")
        plt.title('MS spec for ' + cas_id)
        plt.show()
        """

    pprint(shifted_dict)


def main():
    shift_all_MS()


if __name__ == '__main__':
    main()

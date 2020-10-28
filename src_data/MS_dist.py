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
    molecule_df = pd.read_csv(ms_data_path)

    # Get all the CAS IDs
    CAS_IDS = molecule_df.columns[1:2]
    print(molecule_df.columns[1:])

    CAS_ID = molecule_df.columns[1:2][0]

    bins = molecule_df.index
    ms_spec_data = np.array(molecule_df[CAS_ID])

    print(ms_spec_data)

    """
    plt.plot(range(len(ir_spec_data)), ir_spec_data, color='blue')
    plt.xticks(rotation=-20)
    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False)  # labels along the bottom edge are off
    plt.xlabel("m/z")
    plt.ylabel("Relative Intensity")
    plt.title('MS spec for ' + CAS_ID)
    plt.show()
    """

    """
    for CAS_ID in ['103822']:

        print(CAS_ID)

        bins = molecule_df.index
        ir_spec_data = molecule_df[CAS_ID]

        plt.plot(range(len(ir_spec_data)), ir_spec_data, color='blue')
        plt.xticks(rotation=-20)
        plt.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=False,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=False)  # labels along the bottom edge are off
        plt.xlabel("m/z")
        plt.ylabel("Relative Intensity")
        plt.title('MS spec for ' + CAS_ID)
        plt.show()
    """


mock_ms = np.array([0, 1, 0.5, 0, 2, 5, 0, 3, 0, 0.7, 0, 0, 0, 1, 0, 0])
print(mock_ms)

# Get the maximum array index
max_index = np.argmax(mock_ms)
index_offset_tups = list((abs(max_index - index), value)
                         for index, value in enumerate(mock_ms))
index_offset_tups = sorted(index_offset_tups)
pprint(index_offset_tups)

_, shifted_MS = zip(*index_offset_tups)

shifted_MS = np.array(shifted_MS)
pprint(shifted_MS)

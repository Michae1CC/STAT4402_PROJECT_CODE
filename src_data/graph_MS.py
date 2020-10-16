import os
from pprint import pprint

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

ir_data_path = os.path.join('data', 'MASS_SPEC_DF_LAB.pkl')
molecule_df = pd.read_pickle(ir_data_path)

# pprint(molecule_df)

# ['18699779', '98862', '579431', '103822']
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

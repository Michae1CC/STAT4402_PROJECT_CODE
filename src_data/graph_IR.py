import os
from pprint import pprint

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

ir_data_path = os.path.join('data', 'IR_bins_test.csv')
molecule_df = pd.read_csv(ir_data_path, index_col=0)

CAS_ID = '116668281'
CAS_ID = '51456'
# CAS_ID = '50022'


bins = molecule_df['x']
ir_spec_data = molecule_df[CAS_ID]

bins = [str(bin_) for bin_ in bins][:]

for i in range(len(bins)):
    if i % 10:
        bins[i] = ""

ir_spec_data = ir_spec_data[:]

plt.plot(range(len(ir_spec_data)), ir_spec_data, color='red')
plt.xticks(rotation=-20)
plt.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom=False,      # ticks along the bottom edge are off
    top=False,         # ticks along the top edge are off
    labelbottom=False)  # labels along the bottom edge are off
plt.xlabel("Wavenumber 1/CM")
plt.ylabel("Transmittance")
plt.title('IR spec for ' + CAS_ID)
plt.show()

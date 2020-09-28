import os

import numpy as np
import pandas as pd

from pprint import pprint
from jcamp import JCAMP_reader

import matplotlib.pyplot as plt

MASS_SPEC_PATH = os.path.join('data', 'mass')

x_bins = np.arange(0, 501, 1)
main_df = pd.DataFrame({'x': pd.cut(np.arange(1, 499, 50), x_bins)})
main_df.set_index('x', inplace=True)

for jdx_file in os.listdir(os.path.join('data', 'mass'))[:2]:

    if not jdx_file.endswith('.jdx'):
        continue

    jcamp_dict = JCAMP_reader(os.path.join(MASS_SPEC_PATH, jdx_file))

    x_values = jcamp_dict['x'] * float(jcamp_dict['xfactor'])
    y_values = jcamp_dict['y'] * float(jcamp_dict['yfactor'])

    # Scale by largest y val
    y_values = y_values / max(y_values)

    cas_idx = jcamp_dict['cas registry no'].replace('-', '')

    # Construct a temporary df for the molecule to store its x and y values
    single_df = pd.DataFrame({'x': x_values, cas_idx: y_values})
    single_df['x'] = pd.cut(single_df['x'], x_bins)
    single_df = single_df.groupby('x').aggregate(np.mean).fillna(0)

    plt.bar(list(map(str, single_df.index)), list(single_df[cas_idx]))
    plt.xticks(rotation=90)
    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False)  # labels along the bottom edge are off
    plt.title(cas_idx)
    plt.show()

    main_df = main_df.merge(single_df, on='x', how='outer')

pprint(main_df)

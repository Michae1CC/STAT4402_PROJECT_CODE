import os

import numpy as np
import pandas as pd

from pprint import pprint
from jcamp import JCAMP_reader


def shift_ms_data(x_values, jcamp_dict):
    """
    Shifts the mass spec data by subtracting by the mass of the molecule.
    """

    try:
        # Get the molar mass
        molar_mass = round(float(jcamp_dict['mw']))

    except Exception:
        pprint(jcamp_dict)
        exit(1)

    x_values = molar_mass - x_values

    x_values[x_values < 0] = 0

    return x_values


def create_mass_spec_df(mass_spec_path, x_max_bin=501, mass_shift=False):
    """
    Creates a new data frame for mass spec data.

    Parameters:
        mass_spec_path:
            A path to where all the mass spec jdx files are stored.

        x_max_bin:
            The maximum mass spec value to be captured.

    Return:
        Returns a dataframe where the indexes are mass spec buckets and new
        columns represent new columns.
    """

    x_bins = np.arange(0, x_max_bin, 1)
    main_df = pd.DataFrame({'x': pd.cut(np.arange(1, 499, 50), x_bins)})
    main_df.set_index('x', inplace=True)

    print("extracting data...")

    for jdx_file in os.listdir(mass_spec_path):

        if not jdx_file.endswith('.jdx'):
            continue

        jcamp_dict = JCAMP_reader(os.path.join(mass_spec_path, jdx_file))

        x_values = jcamp_dict['x'] * float(jcamp_dict['xfactor'])
        y_values = jcamp_dict['y'] * float(jcamp_dict['yfactor'])

        cas_idx = jcamp_dict['cas registry no'].replace('-', '')

        if mass_shift:
            x_values = shift_ms_data(x_values, jcamp_dict)

        # Scale by largest y val
        y_values = y_values / max(y_values)

        # Construct a temporary df for the molecule to store its x and y values
        single_df = pd.DataFrame({'x': x_values, cas_idx: y_values})
        single_df['x'] = pd.cut(single_df['x'], x_bins)
        single_df = single_df.groupby('x').aggregate(np.mean).fillna(0)

        main_df = main_df.merge(single_df, on='x', how='outer')

    return main_df


def main():
    MASS_SPEC_PATH = os.path.join('data', 'mass')
    mass_spec_df = create_mass_spec_df(MASS_SPEC_PATH, mass_shift=True)
    # pprint(mass_spec_df)

    # Construct the output path for the dataframe
    DF_PATH = os.path.join('data', 'MASS_SPEC_DF_SHIFT.csv')

    # Pickle the dataframe
    mass_spec_df.to_csv(DF_PATH)


if __name__ == '__main__':
    main()

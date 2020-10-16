import os
import sys
import itertools
import pickle

import numpy as np
import pandas as pd

from pprint import pprint


def load_pd_df(path):

    if path.lower().endswith(".csv"):
        return pd.read_csv(path, index_col=0)

    elif path.lower().endswith(".pkl") or path.lower().endswith(".pickle"):
        return pd.read_pickle(path)

    raise NotImplementedError(
        f"Don't know how to deal with file type of {path}")


def create_aggregate(ir_data_path, ms_data_path, cas_to_func_path):
    """
    Aggregates data from ir, mass spec and CAS to functional group labels
    to form a labelled training set.
    """

    ir_df = load_pd_df(ir_data_path)
    ms_df = load_pd_df(ms_data_path)
    cas_to_func_df = load_pd_df(cas_to_func_path)

    x_labels = []
    y_labels = []

    count = 0

    # Iterate through the indexes of the CAS id
    for cas_id in cas_to_func_df.index:

        count += 1

        if not count % 500:
            print("Completed: ", count, flush=True)

        # Try and get the ir and mass spec data for this cas id
        try:
            cas_id_str = str(cas_id)
            ir_single_data = ir_df[cas_id_str]
            ms_single_data = ms_df[cas_id_str]
        except KeyError:
            # The ir or ms data corresponding to this cas id doesn't exist,
            # move on
            continue

        x_labels.append(list(ir_single_data) + list(ms_single_data))
        y_labels.append(list(cas_to_func_df.loc[cas_id]))

    return np.array(x_labels, dtype=float), np.array(y_labels, dtype=int)


def main():

    # The project is different on getafix
    if sys.platform.startswith('win32'):
        PROJECT_DIR = os.path.join(
            'D:\\', '2020', 'S2', 'STAT_4402', 'ASSESSMENT', 'STAT4402_PROJECT_CODE')
    elif sys.platform.startswith('linux'):
        PROJECT_DIR = os.path.join(
            '/', 'home', 's4430291', 'Courses', 'STAT4402', 'STAT4402_PROJECT_CODE')

    ir_data_path = os.path.join(PROJECT_DIR, 'data', 'IR_bins_LAB.csv')
    mass_spec_data_path = os.path.join(
        PROJECT_DIR, 'data', 'MASS_SPEC_DF_LAB.pkl')
    cas_to_func_path = os.path.join(
        PROJECT_DIR, 'data', 'CAS_TO_FUNC_LAB.csv')

    aggregate_npy_X, aggregate_npy_y = create_aggregate(
        ir_data_path, mass_spec_data_path, cas_to_func_path)

    print(aggregate_npy_X.shape)
    print(aggregate_npy_y.shape)

    aggregate_csv_path_X = os.path.join(
        PROJECT_DIR, 'data', 'IR_MS_FUNCTIONAL_X_LAB.csv')
    aggregate_npy_path_X = os.path.join(
        PROJECT_DIR, 'data', 'IR_MS_FUNCTIONAL_X_LAB.npy')

    aggregate_csv_path_y = os.path.join(
        PROJECT_DIR, 'data', 'IR_MS_FUNCTIONAL_y_LAB.csv')
    aggregate_npy_path_y = os.path.join(
        PROJECT_DIR, 'data', 'IR_MS_FUNCTIONAL_y_LAB.npy')

    # Save the aggregate data as both a npy and csv file
    # np.savetxt(aggregate_csv_path_X, aggregate_npy_X)
    np.save(aggregate_npy_path_X, aggregate_npy_X)

    # np.savetxt(aggregate_csv_path_y, aggregate_npy_y)
    np.save(aggregate_npy_path_y, aggregate_npy_y)


if __name__ == '__main__':
    main()

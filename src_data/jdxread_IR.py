import itertools
import os
import sys
import pickle
from pprint import pprint

import numpy as np
import pandas as pd
from jcamp import JCAMP_reader

from concurrent import futures
import concurrent.futures


def extract_transmittance(jdx_file_path):
    """
    Extracts transmittance from a specified jdx file. Absorbance values are
    automatically converted to transmittance values.

    Parameters:
        jdx_file_path: 
            A file path to the jdx file that contains transmittance data

    Return:
        Returns the following triple
            (cas_id, x, y_transmittance)
    """

    jcamp_dict = JCAMP_reader(jdx_file_path)

    # Make sure units are in centimeters
    if jcamp_dict['xunits'].lower() == 'micrometers':
        jcamp_dict['x'] = 10 ** (4) / jcamp_dict['x']

    if jcamp_dict['yunits'].lower() == 'transmittance':
        # The y values are already in transmittance form, do nothing
        pass

    elif jcamp_dict['yunits'].lower() == 'absorbance':
        # Convert absorbance to transmittance
        jcamp_dict['y'] = np.power(10, 2 - jcamp_dict['y']) / 100

    else:
        raise ValueError("Not equipped to handle IR of type: " +
                         jcamp_dict['yunits'].lower())

    # Get the CAS id for this molecule
    CAS_ID = jcamp_dict['cas registry no'].replace('-', '')

    return CAS_ID, jcamp_dict['x'], jcamp_dict['y']


def thread_func(data_tuple):

    bins, single_dfs = data_tuple

    single_dfs[0]['x'] = pd.cut(single_dfs[0]['x'], bins)
    main_df = single_dfs[0].groupby('x').aggregate(np.mean)
    main_df.reset_index(inplace=True)

    count = 1

    for single_df in single_dfs[1:]:

        count += 1

        if not count % 1000:
            print("thread completed: ", count, flush=True)

        single_df['x'] = pd.cut(single_df['x'], bins)
        single_df = single_df.groupby('x').aggregate(np.mean)
        single_df.reset_index(inplace=True)

        main_df = main_df.merge(single_df, on='x', how='outer')

    return main_df


def get_all_transmittance(IR_path_name=os.path.join('data', 'ir_test'), x_max_bin=4500, num_threads=4):
    """
    Get all the IR transmittance values from the samples within a folder
    containing jdx files.

    Parameters:
        IR_path_name:
            A path to a folder containing all the transmittance data as jdx
            files.

    Return:
    Returns a dictionary with the following structure
        transmittance_dict = {
            cas_is : {
                'x' : np.array([ x_1, x_2 , ... , x_n ])
                'y' : np.array([ y_1, y_2 , ... , y_n ])
            },
            ...
        }
    """

    # transmittance_dict = {}

    # This is just what the paper did to get buckets
    ls = []
    single_dfs = []

    count = 1

    for root, dirs, files in os.walk(IR_path_name):
        for name in files:

            if not count % 1000:
                print(f"Completed: {count} files")

            count += 1

            if name.endswith((".jdx")):

                # Get the full file path to the jdx file
                jdx_file_path = os.path.join(root, name)

                try:
                    # Get the x,y and transmittance values
                    cas_id, x, y = extract_transmittance(jdx_file_path)
                except Exception as e:
                    continue

                # transmittance_dict[cas_id] = {'x': x, 'y': y}

                single_df = pd.DataFrame({'x': x, cas_id: y})
                single_df = single_df.groupby('x').aggregate(np.mean)
                single_df.reset_index(inplace=True)
                single_dfs.append(single_df)

                ls.append([np.min(np.diff(single_df['x'])), np.min(
                    single_df['x']), np.max(single_df['x'])])

    arr = np.array(ls)
    bins = np.arange(np.min(arr[:, 1])-0.1,
                     np.max(arr[:, 2])+0.1, np.mean(arr[:, 0]))

    merged_dfs = []

    single_dfs = np.array(single_dfs, dtype=object)
    single_dfs_partition = np.array_split(single_dfs, num_threads)

    del single_dfs
    del arr
    del ls

    threads_args = [(bins, cols_to_merge)
                    for cols_to_merge in single_dfs_partition]

    merged_dfs = []

    with futures.ThreadPoolExecutor(num_threads) as executor:
        submitted_results = executor.map(thread_func, threads_args)

        for merged_df in submitted_results:
            merged_dfs.append(merged_df)

    main_df = merged_dfs[0]

    for merged_df in merged_dfs[1:]:

        main_df = main_df.merge(merged_df, on='x', how='outer')

    main_df.iloc[:, 1:] = main_df.iloc[:, 1:].interpolate(
        limit_direction='both', axis=0)

    return main_df


def get_transmittance_from_template(template_path, IR_path_name=os.path.join('data', 'ir_LAB')):

    main_df = pd.read_csv(template_path)

    # Construct the intervals using string
    intervals = []

    for interval in main_df['x']:
        interval = interval[1:-1]
        lower, upper = interval.split(',')
        lower, upper = float(lower), float(upper)
        intervals.append(pd.Interval(lower, upper))

    main_df = pd.DataFrame({'x': intervals})
    bins = pd.IntervalIndex(intervals)

    for root, dirs, files in os.walk(IR_path_name):
        for name in files:

            if name.endswith((".jdx")):

                # Get the full file path to the jdx file
                jdx_file_path = os.path.join(root, name)
                cas_id, x, y = extract_transmittance(jdx_file_path)

                single_df = pd.DataFrame({'x': x, cas_id: y})
                single_df = single_df.groupby('x').aggregate(np.mean)
                single_df.reset_index(inplace=True)

                single_df['x'] = pd.cut(single_df['x'], bins)
                single_df = single_df.groupby('x').aggregate(np.mean)
                single_df.reset_index(inplace=True)

                main_df = main_df.merge(single_df, on='x', how='outer')

    main_df.iloc[:, 1:] = main_df.iloc[:, 1:].interpolate(
        limit_direction='both', axis=0)

    return main_df


def get_transmittance():
    dc = {}
    xu, yu = [], []
    for root, dirs, files in os.walk(os.path.join('.', '..', 'data', 'IR')):
        for name in files:
            # temp_dc={}
            if name.endswith((".jdx")):

                jcamp_dict = JCAMP_reader(root+'/'+name)

                # NOTE: filter out data that is not transmittance
                if jcamp_dict['yunits'].lower() != 'transmittance':
                    continue

                jcamp_dict['y'] = jcamp_dict['y'] * jcamp_dict['yfactor']
                jcamp_dict['x'] = jcamp_dict['x'] * jcamp_dict['xfactor']

                # xu.append(jcamp_dict['npoints'])
                dc[name[:-4]] = jcamp_dict
                # ls.append(jcamp_dict['x'].shape[0])


def pickle_transmittance_values():

    # The project is different on getafix
    if sys.platform.startswith('win32'):
        PROJECT_DIR = os.path.join(
            'D:\\', '2020', 'S2', 'STAT_4402', 'ASSESSMENT', 'STAT4402_PROJECT_CODE')
    elif sys.platform.startswith('linux'):
        PROJECT_DIR = os.path.join(
            '/', 'home', 's4430291', 'Courses', 'STAT4402', 'STAT4402_PROJECT_CODE')

    # data path on getafix
    DATA_DIR = os.path.join('/', 'data', 's4430291', 'STAT4402_data')

    if sys.platform.startswith('win32'):
        IR_path_name = os.path.join(PROJECT_DIR, 'data', 'ir_LAB')
    elif sys.platform.startswith('linux'):
        IR_path_name = os.path.join(DATA_DIR, 'data', 'ir')

    TEMPLATE_PATH = os.path.join(PROJECT_DIR, 'data', 'IR_LAB_TEMPLATE.csv')

    transmittance_df = get_transmittance_from_template(TEMPLATE_PATH)

    # transmittance_df = get_all_transmittance(
    #     IR_path_name=IR_path_name, num_threads=1)

    pprint(transmittance_df)

    IR_save_path = os.path.join(PROJECT_DIR, 'data', 'IR_bins_LAB.csv')
    transmittance_df.to_csv(IR_save_path)


def main():
    pickle_transmittance_values()


if __name__ == '__main__':
    main()

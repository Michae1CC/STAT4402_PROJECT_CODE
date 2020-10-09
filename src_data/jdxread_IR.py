import os
# import matplotlib.pyplot as plt
# import pandas as pd
import itertools
import pickle
from collections import Counter
from pprint import pprint

import matplotlib.pyplot as plt
# from scipy import stats
import numpy as np
import pandas as pd
from jcamp import JCAMP_reader


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


def get_all_transmittance(IR_path_name=os.path.join('data', 'ir_test'), x_max_bin=4500):
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

    transmittance_dict = {}

    # This is just what the paper did to get buckets
    ls = []
    single_dfs = []

    for root, dirs, files in os.walk(IR_path_name):
        for name in files:

            if name.endswith((".jdx")):

                # Get the full file path to the jdx file
                jdx_file_path = os.path.join(root, name)

                try:
                    # Get the x,y and transmittance values
                    cas_id, x, y = extract_transmittance(jdx_file_path)
                except Exception:
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

    single_dfs[0]['x'] = pd.cut(single_dfs[0]['x'], bins)
    main_df = single_dfs[0].groupby('x').aggregate(np.mean)
    main_df.reset_index(inplace=True)

    for single_df in single_dfs[1:]:
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

    # with open(os.path.join('.', '..', 'data', 'IR_TRANSMITTANCE.pickle'), 'wb') as handle:
    #     pickle.dump(dc, handle, protocol=pickle.HIGHEST_PROTOCOL)


def get_absorbance():
    dc = {}
    xu, yu = [], []
    for root, dirs, files in os.walk(os.path.join('data', 'ir_test')):
        for name in files:
            # temp_dc={}
            if name.endswith((".jdx")):

                jcamp_dict = JCAMP_reader(root+'/'+name)

                # NOTE: filter out data that is not transmittance
                if jcamp_dict['yunits'].upper() != 'ABSORBANCE':
                    continue

                if name in ['50306.jdx']:
                    print(jcamp_dict['x'])
                    print(jcamp_dict['y'])

                jcamp_dict['y'] = np.power(10, 2 - jcamp_dict['y'])/100

                # xu.append(jcamp_dict['npoints'])
                dc[name[:-4]] = jcamp_dict

                if name in ['50306.jdx']:
                    plt.plot(list(map(str, jcamp_dict['x'])), list(
                        jcamp_dict['y'][::-1]))
                    plt.xticks(rotation=90)
                    plt.tick_params(
                        axis='x',          # changes apply to the x-axis
                        which='both',      # both major and minor ticks are affected
                        bottom=False,      # ticks along the bottom edge are off
                        top=False,         # ticks along the top edge are off
                        labelbottom=False)  # labels along the bottom edge are off
                    plt.title(name)
                    plt.show()

    # pprint(dc)
    # with open(os.path.join('data', 'IR_ABSORBANCE.pickle'), 'wb') as handle:
    #     pickle.dump(dc, handle, protocol=pickle.HIGHEST_PROTOCOL)


def pickle_transmittance_values():

    IR_path_name = os.path.join('data', 'ir')
    transmittance_df = get_all_transmittance(IR_path_name=IR_path_name)

    pprint(transmittance_df)

    IR_save_path = os.path.join('data', 'IR_bins_FINAL.csv')
    transmittance_df.to_csv(IR_save_path)


def main():
    pickle_transmittance_values()


if __name__ == '__main__':
    main()

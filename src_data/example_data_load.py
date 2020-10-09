import os
import pickle

import numpy as np


def example_load():
    """
    Demonstrates an example of loading the data for the project. The
    features vectors for the samples are stored in IR_MS_FUNCTIONAL_X.npy
    while the correspong labels are stored in IR_MS_FUNCTIONAL_y.npy. Labels
    and feature vectors will share the same index. For example the label for
        IR_MS_FUNCTIONAL_X[1412]
    will be
        IR_MS_FUNCTIONAL_y[1412]

    The feature vectors have the form:

        [ ... ir data ... , ... ms data ... ]

    where each entry is a floating point value. The labels will take the form

        [ FUNC_GRP_1 , FUNC_GRP_2 , ... , FUNC_GRP_N ]

    where FUNC_GRP_i is a binary value indicating whether or not that 
    functional group is present.
    """

    x_data_path = os.path.join('data', 'IR_MS_FUNCTIONAL_X.npy')
    y_data_path = os.path.join('data', 'IR_MS_FUNCTIONAL_y.npy')

    IR_MS_FUNCTIONAL_X = np.load(x_data_path)
    IR_MS_FUNCTIONAL_y = np.load(y_data_path)

    print(IR_MS_FUNCTIONAL_X.shape)
    print(IR_MS_FUNCTIONAL_y.shape)

    print()

    print(IR_MS_FUNCTIONAL_X[0])

    print()

    print(IR_MS_FUNCTIONAL_y[0])


def main():
    example_load()


if __name__ == '__main__':
    main()

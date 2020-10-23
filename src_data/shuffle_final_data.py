import os

import numpy as np


def load_and_shuffle(x_data_path, y_data_path):

    if x_data_path.lower().endswith(".csv"):
        IR_MS_FUNCTIONAL_X = np.loadtxt(x_data_path, dtype=float)
    elif x_data_path.lower().endswith(".npy"):
        IR_MS_FUNCTIONAL_X = np.load(x_data_path)
    else:
        raise NotImplementedError(
            f"Don't know how to deal with file type of {x_data_path}")

    if y_data_path.lower().endswith(".csv"):
        IR_MS_FUNCTIONAL_y = np.loadtxt(y_data_path, dtype=int)
    elif y_data_path.lower().endswith(".npy"):
        IR_MS_FUNCTIONAL_y = np.load(y_data_path)
    else:
        raise NotImplementedError(
            f"Don't know how to deal with file type of {y_data_path}")

    print(IR_MS_FUNCTIONAL_X.shape)
    print(IR_MS_FUNCTIONAL_y.shape)

    shuffled_index = np.arange(IR_MS_FUNCTIONAL_X.shape[0])
    np.random.shuffle(shuffled_index)

    IR_MS_FUNCTIONAL_X_shuffle = IR_MS_FUNCTIONAL_X[shuffled_index]
    IR_MS_FUNCTIONAL_y_shuffle = IR_MS_FUNCTIONAL_y[shuffled_index]

    # print(IR_MS_FUNCTIONAL_X_shuffle)
    # print(IR_MS_FUNCTIONAL_y_shuffle)

    # shuffle_path_X = os.path.join('data', 'IR_MS_FUNCTIONAL_X.npy')
    # shuffle_path_y = os.path.join('data', 'IR_MS_FUNCTIONAL_y.npy')

    # np.save(shuffle_path_X, IR_MS_FUNCTIONAL_X_shuffle)
    # np.save(shuffle_path_y, IR_MS_FUNCTIONAL_y_shuffle)


def main():

    x_data_path = os.path.join('data', 'IR_MS_FUNCTIONAL_X.npy')
    y_data_path = os.path.join('data', 'IR_MS_FUNCTIONAL_y.npy')

    load_and_shuffle(x_data_path, y_data_path)


if __name__ == '__main__':

    main()

import os

import numpy as np


def load_project_data(x_data_path: str = 'IR_MS_FUNCTIONAL_X.npy', y_data_path: str = 'IR_MS_FUNCTIONAL_y.npy', train_size: float = None, test_size: float = 0.25):
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

    Parameters:
        x_data_path (str):
            A path string to a file containing the feature vectors. The
            feature values should be stored across columns while the
            samples should be stored across different rows. The file may
            either be a csv of numpy binary file.

        y_data_path (str):
            A path string to a file containing the label vectors. The
            label values should be stored across columns while the
            different samples should be stored across rows. The file may
            either be a csv of numpy binary file.

        train_size (float):
            The ratio of data to include in the training set.

        test_size (float):
            The ratio of data to include in the testing set.

        NOTE:
            If both train_size and test_size are specified then they will be
            treated as a ratio to split the data. For example if train_size = 3
            and test_size = 2 then 3 / 5 of the total data will be dedicated to
            the training set and 2 / 5 will be dedicated to the testing set.
    """

    if train_size < 0 or test_size < 0:
        raise ValueError("test_size and train_size must be positive values.")

    if (train_size is None and test_size is not None):
        if test_size > 1:
            raise ValueError("test_size must be ratio if train_size is None")

    if (test_size is None and train_size is not None):
        if train_size > 1:
            raise ValueError("train_size must be ratio if test_size is None")

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

    train_ratio = None

    # Find the test and train ratios
    if train_size is None and test_size is None:
        # Use the default train ratio of 0.75
        train_ratio = 0.75
    elif train_size is not None and test_size is None:
        train_ratio = train_size
    elif train_size is None and test_size is not None:
        train_ratio = 1 - test_size
    else:
        total = train_size + test_size
        train_ratio = train_size / total

    samples, _ = IR_MS_FUNCTIONAL_X.shape

    # Compute the index at which the split the training set
    train_index = round(samples * train_ratio)

    return IR_MS_FUNCTIONAL_X[:train_index], IR_MS_FUNCTIONAL_X[train_index:], \
        IR_MS_FUNCTIONAL_y[:train_index], IR_MS_FUNCTIONAL_y[train_index:]


def main():
    """
    An example of load the data and print out the shapes of the feature
    vectors and label vectors.
    """

    # NOTE: These paths may need to change, depending on where you've
    # saved IR_MS_FUNCTIONAL_X.npy and IR_MS_FUNCTIONAL_y.npy. If you've
    # saved both npy files in the same directory as this example.py file,
    # just remove 'data' as a parameter to os.path.join and just use
    # os.path.join('IR_MS_FUNCTIONAL_X.npy').
    x_data_path = os.path.join('data', 'IR_MS_FUNCTIONAL_X.npy')
    y_data_path = os.path.join('data', 'IR_MS_FUNCTIONAL_y.npy')

    IR_MS_FUNCTIONAL_X_train, IR_MS_FUNCTIONAL_X_test, IR_MS_FUNCTIONAL_y_train, IR_MS_FUNCTIONAL_y_test = load_project_data(
        x_data_path, y_data_path,
        train_size=2, test_size=0.5
    )

    print("Train shapes")
    print(IR_MS_FUNCTIONAL_X_train.shape)
    print(IR_MS_FUNCTIONAL_y_train.shape)

    print()

    print("Test shapes")
    print(IR_MS_FUNCTIONAL_X_test.shape)
    print(IR_MS_FUNCTIONAL_y_test.shape)

    print()

    print(IR_MS_FUNCTIONAL_X_train[0])
    print()

    print(IR_MS_FUNCTIONAL_y_train[0])
    print()


if __name__ == '__main__':
    main()

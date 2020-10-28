#!/usr/bin/env python3

__author__ = 'Michael Ciccotosto-Camp'
__version__ = ''

# -*- coding: utf-8 -*-
"""best_model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tW8wuUtfZZ_IsqoteS-oXZ48oZnMMJ08
"""

import argparse
import csv
import itertools
import os
import socket
import sys

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from scipy import optimize
from sklearn.metrics import (accuracy_score, average_precision_score, f1_score,
                             precision_recall_curve)
from torch.nn.modules.loss import MSELoss
from torch.utils.data import DataLoader

if sys.platform.startswith('win32'):
    PROJECT_DIR = os.path.join(
        'D:\\', '2020', 'S2', 'STAT_4402', 'ASSESSMENT', 'STAT4402_PROJECT_CODE')
elif sys.platform.startswith('linux'):
    PROJECT_DIR = os.path.join(
        '/', 'home', 's4430291', 'Courses', 'STAT4402', 'STAT4402_PROJECT_CODE')

torch.manual_seed(123)


def convert_bool_arg(arg_in):
    """
    Converts a boolean command line argument into a python boolean object.

    Parameters:
        arg_in:
            The given command line argument.

    Return:
        The interrupted boolean value of the command line argument.
    """

    false_options = ('f', 'false', '0', 'n', 'no', 'nan', 'none')

    if arg_in.lower() in false_options:
        return False

    return True


parser = argparse.ArgumentParser(
    description="Runs MLP with a single hyperparameter combination.")

parser.add_argument('--latent_dim', type=int, default=300,
                    help='The total number of latent dims (IR+MS).')
parser.add_argument('--MS_ratio', type=float, default=0.1,
                    help='What proportion of the latent dims should be attributed to MS.')
parser.add_argument('--auto_lr', type=float, default=0.0001,
                    help='Learning rate or auto encoder.')
parser.add_argument('--auto_epoch_num', type=int, default=100,
                    help='The number of epochs to use.')
parser.add_argument('--auto_batch_size', type=int, default=50,
                    help='The batch size to use.')

parser.add_argument('--lr', type=float, default=0.0001,
                    help='Learning rate.')
parser.add_argument('--epoch_num', type=int, default=20,
                    help='The number of epochs to use.')
parser.add_argument('--batch_size', type=int, default=150,
                    help='The batch size to use.')
parser.add_argument('--hidden_layer_2_bool', type=convert_bool_arg, default=False, const=True, nargs='?',
                    help='Use a second hidden layer.')
parser.add_argument('--unit_1_layers', type=int, default=400,
                    help='Number of neurons in the first hidden layer.')
parser.add_argument('--unit_2_layers', type=int, default=250,
                    help='Number of neurons in the second hidden layer.')
parser.add_argument('--unit_3_layers', type=int, default=250,
                    help='Number of neurons in the third hidden layer.')

args = parser.parse_args()

lr = 0.0005
# epoch_num = 250
epoch_num = 20
batch_size = 100
HiddenLayer2Bool = True
Unit1Layers = 400
Unit2Layers = 250
Unit3Layers = 0

# best test perfection 576, 896, 451, 596
latent_dim = 600
MS_ratio = 0.2
auto_lr = 0.0001
auto_epoch_num = 200
auto_batch_size = 50

ms_latent_dim = round(MS_ratio * latent_dim)
ir_latent_dim = latent_dim - ms_latent_dim

print("\n\n")
print("--------------------------------")
print("PARAMETERS:")
print("latent_dim:", latent_dim)
print("MS_ratio:", MS_ratio)
print("auto_lr:", auto_lr)
print("auto_epoch_num:", auto_epoch_num)
print("auto_batch_size:", auto_batch_size)
print("--------------------------------")
print("\n\n", flush=True)


def load_project_data(x_data_path: str = 'IR_MS_FUNCTIONAL_X.npy', y_data_path: str = 'IR_MS_FUNCTIONAL_y.npy', train_size: float = None, test_size: float = None):
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
            The ratio of data to include in the training set. By default
            0.75 samples are dedicated to the training set. 

        test_size (float):
            The ratio of data to include in the testing set. By default
            0.25 samples are dedicated to the testing set. 

    Return:
        Returns the tuple
            x_train, x_test, y_train, y_test

        NOTE:
            If both train_size and test_size are specified then they will be
            treated as a ratio to split the data. For example if train_size = 3
            and test_size = 2 then 3 / 5 of the total data will be dedicated to
            the training set and 2 / 5 will be dedicated to the testing set.
    """
    if train_size is not None:
        if train_size < 0:
            raise ValueError(
                "test_size and train_size must be positive values.")

    if test_size is not None:
        if test_size < 0:
            raise ValueError(
                "test_size and train_size must be positive values.")

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


x_data_path = os.path.join(
    PROJECT_DIR, 'data', 'IR_MS_FUNCTIONAL_X_ALDE.npy')
y_data_path = os.path.join(
    PROJECT_DIR, 'data', 'IR_MS_FUNCTIONAL_y_ALDE.npy')

X, X_test, Y, Y_test = load_project_data(
    x_data_path, y_data_path, train_size=0.8)

# Split the training data into IR and MS groups
X_IR = X[:, :-500]
X_MS = X[:, -500:]

torch.manual_seed(123)


# Build a class for the neural network - for the ae_mlp
class Net2(nn.Module):

    global Unit1Layers
    global Unit2Layers

    def __init__(self):
        super(Net2, self).__init__()

        # layer 1
        self.hidden1 = nn.Sequential(nn.Linear(latent_dim, Unit1Layers),  # no. latent variables
                                     nn.ReLU())

        # layer 2
        self.hidden2 = nn.Sequential(nn.Linear(Unit1Layers, Unit2Layers),
                                     nn.ReLU())

        # output
        self.output = nn.Linear(Unit2Layers, Y.shape[1])

    def forward(self, x):
        x = self.hidden1(x)
        x = self.hidden2(x)
        x = self.output(x)
        x = torch.sigmoid(x)
        return x


class Net3(nn.Module):

    global Unit1Layers
    global Unit2Layers
    global Unit3Layers

    def __init__(self):
        super(Net3, self).__init__()

        # layer 1
        self.hidden1 = nn.Sequential(nn.Linear(latent_dim, Unit1Layers),  # no. latent variables
                                     nn.ReLU())

        # layer 2
        self.hidden2 = nn.Sequential(nn.Linear(Unit1Layers, Unit2Layers),
                                     nn.ReLU())

        # layer 3
        self.hidden3 = nn.Sequential(nn.Linear(Unit2Layers, Unit3Layers),
                                     nn.ReLU())

        self.output = nn.Linear(Unit3Layers, Y.shape[1])

    def forward(self, x):
        x = self.hidden1(x)
        x = self.hidden2(x)
        x = self.hidden3(x)
        x = self.output(x)
        x = torch.sigmoid(x)
        return x

# Define an auto-encoder for IR only data


class autoencode_IR(nn.Module):
    def __init__(self):
        super(autoencode_IR, self).__init__()

        self.encoder = nn.Sequential(
            nn.Linear(X_IR.shape[1], ir_latent_dim), nn.ReLU())
        self.decoder = nn.Linear(ir_latent_dim, X_IR.shape[1])

    def forward(self, x):
        latent = self.encoder(x)
        decoded = self.decoder(latent)
        decoded = torch.sigmoid(decoded)
        return decoded, latent

# Define an auto-encoder for MS only data


class autoencode_MS(nn.Module):
    def __init__(self):
        super(autoencode_MS, self).__init__()

        self.encoder = nn.Sequential(
            nn.Linear(X_MS.shape[1], ms_latent_dim), nn.ReLU())
        self.decoder = nn.Linear(ms_latent_dim, X_MS.shape[1])

    def forward(self, x):
        latent = self.encoder(x)
        decoded = self.decoder(latent)
        decoded = torch.sigmoid(decoded)
        return decoded, latent

# Train the auto-encoder for the IR data


IR_loss = []


def ae_train_IR(X_IR=X_IR,
                loss_function=nn.MSELoss(),
                epoch_num=auto_epoch_num,
                batch_size=auto_batch_size,
                lr=auto_lr):

    X_in, X_out = torch.tensor(X_IR, dtype=torch.float), torch.tensor(
        X_IR, dtype=torch.float)

    network = autoencode_IR()

    data_tuple = [[X_in[i], X_out[i]] for i in range(len(X_in))]  # accuracy

    batch = torch.utils.data.DataLoader(data_tuple,
                                        batch_size=batch_size,
                                        shuffle=True)

    optimizer = optim.Adam(network.parameters(),
                           lr=lr,
                           betas=(0.9, 0.999))

    for epoch in range(epoch_num):

        running_loss = 0

        for batch_shuffle in batch:

            x, y = batch_shuffle

            # Give loss
            optimizer.zero_grad()
            out, _ = network(x)  # to get the decoded stuff only
            loss = loss_function(out, y)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        print("Iteration: ", epoch + 1,
              ". Running loss: ", running_loss/batch_size)

        IR_loss.append(running_loss/batch_size)

    return network


trained_autoencoder_IR = ae_train_IR()

MS_loss = []

# Train the auto-encoder for the MS data


def ae_train_MS(X_MS=X_MS,
                loss_function=nn.MSELoss(),
                epoch_num=auto_epoch_num,
                batch_size=auto_batch_size,
                lr=auto_lr):

    X_in, X_out = torch.tensor(X_MS, dtype=torch.float), torch.tensor(
        X_MS, dtype=torch.float)

    network = autoencode_MS()

    data_tuple = [[X_in[i], X_out[i]] for i in range(len(X_in))]  # accuracy

    batch = torch.utils.data.DataLoader(data_tuple,
                                        batch_size=batch_size,
                                        shuffle=True)

    optimizer = optim.Adam(network.parameters(),
                           lr=lr,
                           betas=(0.9, 0.999))

    for epoch in range(epoch_num):

        running_loss = 0

        for batch_shuffle in batch:

            x, y = batch_shuffle

            # Give loss
            optimizer.zero_grad()
            out, _ = network(x)  # to get the decoded stuff only
            loss = loss_function(out, y)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        print("Iteration: ", epoch + 1,
              ". Running loss: ", running_loss/batch_size)

        MS_loss.append(running_loss/batch_size)

    return network


trained_autoencoder_MS = ae_train_MS()

MLP_loss = []


def train(X,
          Y=Y,
          loss_function=nn.BCELoss(),
          epoch_num=epoch_num,
          batch_size=batch_size,
          lr=lr,
          HiddenLayer2Bool=HiddenLayer2Bool):

    X, Y = torch.tensor(X, dtype=torch.float), torch.tensor(
        Y, dtype=torch.float)

    if HiddenLayer2Bool:
        network = Net2()
    else:
        network = Net3()

    data_tuple = [[X[i], Y[i]] for i in range(len(X))]  # accuracy

    batch = torch.utils.data.DataLoader(data_tuple,
                                        batch_size=batch_size,
                                        shuffle=True)

    optimizer = optim.Adam(network.parameters(),
                           lr=lr,
                           betas=(0.9, 0.999))

    for epoch in range(epoch_num):

        running_loss = 0

        for batch_shuffle in batch:

            x, y = batch_shuffle

            # Give loss
            optimizer.zero_grad()
            loss = loss_function(network(x), y)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        print("Iteration: ", epoch + 1,
              ". Running loss: ", running_loss/batch_size)

        MLP_loss.append(running_loss/batch_size)

    return network


# make the X_IR and X_MS data into tensors
X_IR = torch.tensor(X_IR, dtype=torch.float)
X_MS = torch.tensor(X_MS, dtype=torch.float)
print(X_IR.shape)
print(X_MS.shape)
X_cat = torch.cat((X_IR, X_MS), 1)
X_cat.shape

# Now set both trained models to evaluation mode
trained_autoencoder_IR.eval()
trained_autoencoder_MS.eval()
# then extract all the relevant latent variables
_, latentIR = trained_autoencoder_IR(X_IR)
_, latentMS = trained_autoencoder_MS(X_MS)
# combine both of these to create one feature vector of the new latent variables
latent_all = torch.cat((latentIR, latentMS), 1)
latent_all.shape

# train the MLP using the latent variables
ae_mlp_network = train(X=latent_all)

# Allow evaluation
network = ae_mlp_network
network.eval()
X = latent_all

X, Y = torch.tensor(X, dtype=torch.float), torch.tensor(Y, dtype=torch.float)

# Get data for evaluating
Y_true = Y.detach().numpy()
Y_scores = [network(X[i]).detach().numpy() for i in range(len(X))]

# Molecular perfection/ Accuracy Functions


def perfect_acc(cutoff, X=X, Y_scores=Y_scores, Y_true=Y_true):
    return -sum([np.array_equal(np.array(Y_scores[i] > cutoff, dtype=int),
                                Y_true[i]) for i in range(len(X))]) / len(X)


def perfect_acc_sep(cutoff, func_group=0, X=X, Y_scores=Y_scores, Y_true=Y_true):
    return -sum([np.array_equal(np.array(Y_scores[i][func_group] > cutoff, dtype=int),
                                Y_true[i][func_group]) for i in range(len(X))]) / len(X)


# Optimal threshold for accuracy of each functional group
optimal_thres_perf = [optimize.fminbound(perfect_acc_sep, 0.0, 0.95, args=(
    func_grp, Y_scores, Y_true)) for func_grp in range(len(Y_scores[0]))]

# F1 score Functions


def f1_sep(func_group=0, eps=1e-7, Y_scores=Y_scores, Y_true=Y_true):
    pre, rec, thre = precision_recall_curve(Y_true[:, func_group],
                                            [Y_scores[i][func_group]
                                             for i in range(np.shape(Y_scores)[0])])
    f1 = 2*pre*rec/(pre+rec+eps)
    max_ind = np.argmax(f1)
    thresholds = thre[max_ind]
    return thresholds, f1[max_ind]


# Optimal threshold for f1 score
optimal_thres_f1 = [f1_sep(func_grp)[0]
                    for func_grp in range(len(Y_scores[0]))]

FUNC_GROUPS = [
    "Alkene".replace(" ", "_").lower(),
    "Alkyne".replace(" ", "_").lower(),
    "Arene".replace(" ", "_").lower(),
    "Ketone".replace(" ", "_").lower(),
    "Ester".replace(" ", "_").lower(),
    "Amide".replace(" ", "_").lower(),
    "Carboxylic_acid".replace(" ", "_").lower(),
    "Alcohol".replace(" ", "_").lower(),
    "Amine".replace(" ", "_").lower(),
    "Nitrile".replace(" ", "_").lower(),
    "Alkyl_halide".replace(" ", "_").lower(),
    "Acyl_Halide".replace(" ", "_").lower(),
    "Ether".replace(" ", "_").lower(),
    "Nitro".replace(" ", "_").lower(),
    "Methyl".replace(" ", "_").lower(),
    "Alkane".replace(" ", "_").lower(),
    "Aldehyde".replace(" ", "_").lower(),
]

# Overall metric function


def metric_func(
        Y_scores,
        Y_true,
        X,
        thres_perf=optimal_thres_f1,
        thres_f1=optimal_thres_f1):  # optimal_thres_f1

    print("\nAverage Precison Score: ",
          average_precision_score(Y_true, Y_scores))

    print("\nMolecular Perfection rate: ", -
          perfect_acc(thres_perf, Y_scores=Y_scores, Y_true=Y_true, X=X))

    print('\nMolecular F1:', f1_score(Y_true,
                                      [np.array(Y_scores[i] > thres_f1, dtype=int)
                                       for i in range(len(Y_scores))],
                                      average='samples', zero_division=0))


print("\n\nTRAIN data meterics:")
# Train data metric
metric_func(Y_scores, Y_true, X)

# Get test data for evaluating
X, X_test, Y, Y_test = load_project_data(
    x_data_path, y_data_path, train_size=0.8)
X_test = torch.tensor(X_test, dtype=torch.float)
X_test_IR = X_test[:, :-500]
X_test_MS = X_test[:, -500:]

_, latent_test_IR = trained_autoencoder_IR(X_test_IR)
_, latent_test_MS = trained_autoencoder_MS(X_test_MS)
latent_test = torch.cat((latent_test_IR, latent_test_MS), 1)
X_test = latent_test
Y_test = torch.tensor(Y_test, dtype=torch.float)

Y_true_test = Y_test.detach().numpy()
Y_scores_test = [network(X_test[i]).detach().numpy()
                 for i in range(len(X_test))]

print("\n\nTEST data meterics:")
# Test data metric
metric_func(Y_scores_test, Y_true_test, X_test)
print("", flush=True)

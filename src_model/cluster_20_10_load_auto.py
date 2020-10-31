#!/usr/bin/env python3

__author__ = 'Michael Ciccotosto-Camp'
__version__ = ''

# -*- coding: utf-8 -*-
"""Cluster_20_10.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lEz-tJL6qum7kdCe_GVnju6SlcMncQs7
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

parser.add_argument('-a', '--adam', type=convert_bool_arg, default=True, const=True, nargs='?',
                    help='Use adam.')
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

lr = args.lr
epoch_num = args.epoch_num
batch_size = args.batch_size
HiddenLayer2Bool = args.hidden_layer_2_bool
Unit1Layers = args.unit_1_layers
Unit2Layers = args.unit_2_layers
Unit3Layers = args.unit_3_layers

print("\n\n")
print("--------------------------------")
print("PARAMETERS:")
print("lr:", lr)
print("epoch_num:", epoch_num)
print("batch_size:", batch_size)
print("HiddenLayer2Bool:", HiddenLayer2Bool)
print("Unit1Layers:", Unit1Layers)
print("Unit2Layers:", Unit2Layers)
print("Unit3Layers:", Unit3Layers)
print("--------------------------------")
print("\n\n", flush=True)


def load_project_data(x_data_path: str = 'IR_MS_FUNCTIONAL_X.npy', y_data_path: str = 'IR_MS_FUNCTIONAL_y.npy',
                      train_size: float = None, test_size: float = None):

    if train_size is not None and train_size < 0:
        raise ValueError("train_size must be positive values.")

    if test_size is not None and test_size < 0:
        raise ValueError("test_size must be positive values.")

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

    if (train_size == 1 and test_size is None) or (test_size == 1 and train_size is None):
        return IR_MS_FUNCTIONAL_X, IR_MS_FUNCTIONAL_y

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


# Build a class for the neural network - for the ae_mlp
class Net2(nn.Module):

    global Unit1Layers
    global Unit2Layers

    def __init__(self):
        super(Net2, self).__init__()

        # layer 1
        self.hidden1 = nn.Sequential(nn.Linear(500, Unit1Layers),  # 500 = no. latent variables
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
        self.hidden1 = nn.Sequential(nn.Linear(500, Unit1Layers),  # 500 = no. latent variables
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


def train_MLP(X,
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

    batch = DataLoader(data_tuple,
                       batch_size=batch_size,
                       shuffle=True)

    optimizer = optim.Adam(network.parameters(),
                           lr=lr,
                           betas=(0.9, 0.999))

    for epoch in range(epoch_num):

        if not epoch % 20:
            print("Iteration: ", epoch + 1, "Completion: ",
                  (epoch+1)/epoch_num, flush=True)

        for batch_shuffle in batch:

            x, y = batch_shuffle

            # Give loss
            optimizer.zero_grad()
            loss = loss_function(network(x), y)
            loss.backward()
            optimizer.step()

    return network


# Load latent variables
x_train_data_path_auto = os.path.join(
    PROJECT_DIR, 'data', 'IR_MS_FUNCTIONAL_X_train_ALDE_AUTO_500.npy')
x_test_data_path_auto = os.path.join(
    PROJECT_DIR, 'data', 'IR_MS_FUNCTIONAL_X_test_ALDE_AUTO_500.npy')

latent = np.load(x_train_data_path_auto)
latent = torch.tensor(latent, dtype=torch.float)

X_test = np.load(x_test_data_path_auto)
X_test = torch.tensor(X_test, dtype=torch.float)

ae_mlp_network = train_MLP(X=latent)


# Allow evaluation
network = ae_mlp_network
network.eval()
X = latent

X, Y = torch.tensor(X, dtype=torch.float), torch.tensor(Y, dtype=torch.float)

# Get data for evaluating
Y_true = Y.detach().numpy()
Y_scores = [network(X[i]).detach().numpy() for i in range(len(X))]

# Molecular perfection/ Accuracy Functions


def perfect_acc(cutoff, X=X, Y_scores=Y_scores, Y_true=Y_true, lambda_=0):
    # The lambda is a regularization parameter for the threshold, this will
    # punish the optimizer for choosing thresholds far away from 0.5.

    # NOTE that regularization is turned off by default
    return -sum([np.array_equal(np.array(Y_scores[i] > cutoff, dtype=int),
                                Y_true[i]) for i in range(len(X))]) / len(X) + lambda_ * np.linalg.norm(cutoff - 0.5)


def perfect_acc_sep(cutoff, func_group=0, X=X, Y_scores=Y_scores, Y_true=Y_true, lambda_=0):
    # The lambda is a regularization parameter for the threshold, this will
    # punish the optimizer for choosing thresholds far away from 0.5.

    # NOTE that regularization is turned off by default
    return -sum([np.array_equal(np.array(Y_scores[i][func_group] > cutoff, dtype=int),
                                Y_true[i][func_group]) for i in range(len(X))]) / len(X) + lambda_ * np.linalg.norm(cutoff - 0.5)


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
    "Alkane".replace(" ", "_").lower(),
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

Y_test = torch.tensor(Y_test, dtype=torch.float)
Y_true_test = Y_test.detach().numpy()

Y_scores_test = [network(X_test[i]).detach().numpy()
                 for i in range(len(X_test))]

print("\n\nTEST data meterics:")
# Test data metric
metric_func(Y_scores_test, Y_true_test, X_test)
print("", flush=True)

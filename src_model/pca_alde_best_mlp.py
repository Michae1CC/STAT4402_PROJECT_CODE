# -*- coding: utf-8 -*-
"""PCA_ALDE_best_MLP.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15Gaq2r6sLd0q0k3IwukRpbemjevgxLEQ
"""

from tqdm import tqdm
from sklearn.model_selection import StratifiedKFold,KFold,GroupKFold
from sklearn.decomposition import PCA

import os
import numpy as np

# Mount the STAT4402 drive to access feature space data and labels
from google.colab import drive
drive.mount('/content/drive')

def load_project_data(x_data_path: str = 'IR_MS_FUNCTIONAL_X_ALDE.npy', y_data_path: str = 'IR_MS_FUNCTIONAL_y_ALDE.npy', train_size: float = None, test_size: float = None):
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
          raise ValueError("test_size and train_size must be positive values.")

    if test_size is not None:
      if test_size < 0:
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

x_data_path = os.path.join('/content/drive', 'My Drive', 'STAT4402_PROJECT', 'IR_MS_FUNCTIONAL_X_ALDE.npy')
y_data_path = os.path.join('/content/drive', 'My Drive', 'STAT4402_PROJECT', 'IR_MS_FUNCTIONAL_y_ALDE.npy')

X, X_test, Y, Y_test = load_project_data(x_data_path, y_data_path, train_size = 0.8)

# Create a separate sklearn PCA model for the IR and MS data

# Reduce the IR feature space from 4537 to 2700 components
pca_model = PCA(n_components=3000)

# Fit the auto encoders with the training data
pca_model.fit(X)

# Fit the trained PCA to the respctive IR and MS data
X = pca_model.transform(X)
X_test = pca_model.transform(X_test)

sum(pca_model.explained_variance_)

lr	= 0.0005
epoch_num = 200
batch_size = 100	
HiddenLayer2Bool	= True
Unit1Layers	= 400
Unit2Layers	= 250
Unit3Layers = 0

print(X.shape)
print(X_test.shape)

import torch
import torch.nn as nn
import torch.optim as optim
from torch.nn.modules.loss import MSELoss
torch.manual_seed(123)


# Build a class for the neural network - for the ae_mlp 
class Net2(nn.Module):

  global Unit1Layers
  global Unit2Layers

  def __init__(self):
    super(Net2,self).__init__()

    #layer 1
    self.hidden1 = nn.Sequential(nn.Linear(3000, Unit1Layers), # 3000 = no. latent variables
                               nn.ReLU())

    #layer 2
    self.hidden2 = nn.Sequential(nn.Linear(Unit1Layers,Unit2Layers), 
                               nn.ReLU())

    #output
    self.output = nn.Linear(Unit2Layers, Y.shape[1])

  def forward(self,x):
    x = self.hidden1(x)
    x = self.hidden2(x)
    x = self.output(x)
    x = torch.sigmoid(x)
    return x

# #Without batches/epoch

# net = Net()

# X = torch.tensor(IR_MS_FUNCTIONAL_X, dtype=torch.float)
# Y = torch.tensor(IR_MS_FUNCTIONAL_y,dtype=torch.int)

# optimizer = optim.Adam(net.parameters(),lr=0.00015, betas=(0.9, 0.999))
# criterion = nn.BCELoss()

# for i in tqdm(range(500)):
#   optimizer.zero_grad()
#   loss = criterion(net(X),Y)
#   loss.backward()
#   optimizer.step()

def train(X = X,
          Y = Y,    
          loss_function=nn.BCELoss(),
          epoch_num = 100,  
          batch_size= 50,
          lr=0.00015,):
  

  X,Y = torch.tensor(X, dtype=torch.float),torch.tensor(Y,dtype=torch.float)

  network = Net2()

  data_tuple = [[X[i], Y[i]] for i in range(len(X))] #accuracy 

  batch = torch.utils.data.DataLoader(data_tuple, 
                                      batch_size=batch_size, 
                                      shuffle=True)
  
  optimizer = optim.Adam(network.parameters(), 
                         lr=lr,
                         betas=(0.9, 0.999))

  for epoch in range(epoch_num):

    if not epoch % 10:
      print("Iteration: ", epoch +1, "Completion: ", (epoch+1)/epoch_num)
    
    for batch_shuffle in batch:
      
      x,y = batch_shuffle

      #Give loss
      optimizer.zero_grad()
      loss = loss_function(network(x),y)
      loss.backward()
      optimizer.step()

  return network

network = train(X)

X.shape

from sklearn.metrics import average_precision_score
from sklearn.metrics import precision_recall_curve,f1_score, accuracy_score
from scipy import optimize

#Allow evaluation
network.eval()

X,Y = torch.tensor(X, dtype=torch.float),torch.tensor(Y,dtype=torch.float)

#Get data for evaluating 
Y_true = Y.detach().numpy()
Y_scores =  [network(X[i]).detach().numpy() for i in range(len(X))]

#Molecular perfection/ Accuracy Functions 

def perfect_acc(cutoff, X = X, Y_scores = Y_scores, Y_true = Y_true):
  return -sum([np.array_equal(np.array(Y_scores[i] > cutoff, dtype=int), 
                              Y_true[i]) for i in range(len(X))]) /len(X)

def perfect_acc_sep(cutoff, func_group=0, X=X, Y_scores= Y_scores, Y_true= Y_true):
  return -sum([np.array_equal(np.array(Y_scores[i][func_group] > cutoff, dtype=int), 
                              Y_true[i][func_group]) for i in range(len(X))]) /len(X)

#Optimal threshold for accuracy of each functional group
optimal_thres_perf = [optimize.fminbound(perfect_acc_sep, 0.0, 0.95, args=(func_grp,Y_scores, Y_true)) for func_grp in range(len(Y_scores[0]))]

#F1 score Functions 

def f1_sep(func_group = 0, eps = 1e-7, Y_scores = Y_scores, Y_true = Y_true):
  pre,rec,thre = precision_recall_curve(Y_true[:,func_group],
                                        [Y_scores[i][func_group] 
                                         for i in range(np.shape(Y_scores)[0])])
  f1 = 2*pre*rec/(pre+rec+eps)
  max_ind = np.argmax(f1)
  thresholds = thre[max_ind]
  return thresholds, f1[max_ind]

#Optimal threshold for f1 score
optimal_thres_f1 = [f1_sep(func_grp)[0] for func_grp in range(len(Y_scores[0]))]

from tabulate import tabulate
import pandas as pd

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

#Overall metric function
def metric_func(
    Y_scores,
    Y_true,
    X, 
    thres_perf = optimal_thres_perf,
    thres_f1 = optimal_thres_perf):  #optimal_thres_f1
  
  print("\nAverage Precison Score: ", average_precision_score(Y_true, Y_scores))

  print("\nAccuracy for each functional group:\n ")
        # [-perfect_acc_sep(thres_perf[i], i, Y_scores = Y_scores, Y_true = Y_true) for i in range(len(Y[0]))])
  df_acc = pd.DataFrame({'Functional' :FUNC_GROUPS,
                   'Accuracy' : [-perfect_acc_sep(thres_perf[i], i, Y_scores = Y_scores, Y_true = Y_true, X=X) for i in range(len(Y[0]))]})
  print(tabulate(df_acc, headers='keys', tablefmt='psql'))

  
  print("\nMolecular Perfection rate: ", -perfect_acc(thres_perf,Y_scores = Y_scores, Y_true = Y_true, X=X))

  print('\nFunctional Group F1:')
  
  df_f1 = pd.DataFrame({'Functional' :FUNC_GROUPS,
                   'F1' : f1_score(Y_true, [np.array(Y_scores[i] > thres_f1, dtype=int) for i in range(len(Y_scores))],average = None)})
  print(tabulate(df_f1, headers='keys', tablefmt='psql'))
  
  print('\nMolecular F1:', f1_score(Y_true, 
        [np.array(Y_scores[i] > thres_f1, dtype=int) 
        for i in range(len(Y_scores))],
        average = 'samples', zero_division = 0))

# Train data metric
metric_func(Y_scores,Y_true, X)

#Get test data for evaluating 
X_test = torch.tensor(X_test, dtype=torch.float)
Y_test = torch.tensor(Y_test,dtype=torch.float)

Y_true_test = Y_test.detach().numpy()
Y_scores_test =  [network(X_test[i]).detach().numpy() for i in range(len(X_test))]

#Test data metric
metric_func(Y_scores_test,Y_true_test, X_test)
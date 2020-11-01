# -*- coding: utf-8 -*-
"""CNN_project_STAT4402.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/174-urdMvJ9SwxW6L9gbh_mv919wt5gIr
"""

from tqdm import tqdm
from sklearn.model_selection import StratifiedKFold,KFold,GroupKFold

import os
import numpy as np

# Mount the STAT4402 drive to access feature space data and labels
from google.colab import drive
drive.mount('/content/drive')

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

x_data_path = os.path.join('/content/drive', 'My Drive', 'STAT4402_PROJECT', 'IR_MS_FUNCTIONAL_X.npy')
y_data_path = os.path.join('/content/drive', 'My Drive', 'STAT4402_PROJECT', 'IR_MS_FUNCTIONAL_y.npy')

X, X_test, Y, Y_test = load_project_data(x_data_path, y_data_path, train_size = 0.8)

X.shape[1]

#https://stackoverflow.com/questions/60591140/i-dont-understand-pytorch-input-sizes-of-conv1d-conv2d

import torch
import torch.nn as nn
import torch.optim as optim
from torch.nn.modules.loss import MSELoss
torch.manual_seed(123)


# Build a class for the neural network 
class Net(nn.Module):
  def __init__(self):
    super(Net,self).__init__()


    #paramaters 
    kernel = 30
    C1 = 2
    stride = 1
    X_shape = 500
    out1 = C1*int(np.floor((X_shape - kernel)/stride +1).item())

    kernel2 = 10
    C2 = 1
    out2 = 424 #C2*int(np.floor((out1 - kernel2)/stride +1).item())

    F1=50

    #CNN
    #[Batch, chan1, X.shape[1]]
    self._net_convolution1 = nn.Sequential(nn.Conv1d(in_channels=1, 
                                                    out_channels=C1, 
                                                    kernel_size=kernel), 
                                          nn.ReLU())
    
    self._net_maxpool1 = nn.MaxPool1d(kernel_size = kernel, stride = stride)
    self.normalisation1 = nn.BatchNorm1d(out1)


    self._net_convolution2 = nn.Sequential(nn.Conv1d(in_channels=C1, 
                                                    out_channels=C2, 
                                                    kernel_size=kernel2), 
                                          nn.ReLU())
    
    self.normalisation2 = nn.BatchNorm1d(out2)
    self._net_maxpool2 = nn.MaxPool1d(kernel_size = kernel2, stride = stride)


    self._net_feature = nn.Linear(in_features= out2, out_features=F1)
    self.normalisation2 = nn.BatchNorm1d(F1)

    self._out = nn.Sequential(
                            nn.Linear(in_features=F1, out_features=Y.shape[1]),
                            nn.ReLU())

  def forward(self, x):
    # Construct net
    x = self._net_convolution1(x) #conv layers
    x = self._net_maxpool1(x) #max pool
    # x = self.normalisation1(x)
    x = self._net_convolution2(x) #conv layers
    x = self._net_maxpool2(x) #max pool
    # x = self.normalisation2(x)
    x = x.flatten(1)
    x = self._net_feature(x) 
    x = self._out(x) #output
    x = torch.sigmoid(x)

    return x

# Create a class for the autoencoder

class autoencode(nn.Module):
  def __init__(self):
    super(autoencode,self).__init__()

    self.encoder = nn.Sequential(nn.Linear(X.shape[1],500),nn.ReLU())
    self.decoder = nn.Linear(500,X.shape[1])


  def forward(self,x):
    latent = self.encoder(x)
    decoded = self.decoder(latent)
    decoded = torch.sigmoid(decoded)
    return decoded, latent

# write a function to train the autoencoder with
def ae_train(X = X,    
          loss_function=nn.MSELoss(),
          epoch_num = 100,  
          batch_size= 50,
          lr=0.001,):
  

  X_in,X_out = torch.tensor(X, dtype=torch.float),torch.tensor(X,dtype=torch.float)

  network = autoencode()

  data_tuple = [[X_in[i], X_out[i]] for i in range(len(X_in))] #accuracy 

  batch = torch.utils.data.DataLoader(data_tuple, 
                                      batch_size=batch_size, 
                                      shuffle=True)
  
  optimizer = optim.Adam(network.parameters(), 
                         lr=lr,
                         betas=(0.9, 0.999))

  for epoch in range(epoch_num):
    print("Iteration: ", epoch +1, "Completion: ", (epoch+1)/epoch_num)
    for batch_shuffle in batch:
      
      x,y = batch_shuffle

      #Give loss
      optimizer.zero_grad()
      out, _ = network(x) # to get the decoded stuff only
      loss = loss_function(out,y)
      loss.backward()
      optimizer.step()

  return network

def train(X = X,
          Y = Y,    
          loss_function=nn.BCELoss(),
          epoch_num = 100,  
          batch_size= 50,
          lr=0.00015,):
  

  X,Y = torch.tensor(X, dtype=torch.float),torch.tensor(Y,dtype=torch.float)

  network = Net()

  data_tuple = [[X[i], Y[i]] for i in range(len(X))] #accuracy 

  batch = torch.utils.data.DataLoader(data_tuple, 
                                      batch_size=batch_size, 
                                      shuffle=True)
  
  optimizer = optim.Adam(network.parameters(), 
                         lr=lr,
                         betas=(0.9, 0.999))

  for epoch in range(epoch_num):
    print("Iteration: ", epoch +1, "Completion: ", (epoch+1)/epoch_num)
    for batch_shuffle in batch:
      

      
      x,y = batch_shuffle
      x = x.unsqueeze(1)

      #print(2*np.floor(x.size(2) / 3))


      #Give loss
      optimizer.zero_grad()
      loss = loss_function(network(x),y)
      loss.backward()
      optimizer.step()

  return network

#Train Autoencoder
trained_autoencoder = ae_train()

#The above will be loaded in when being sent to the cluster instead of training for 
#each iteration....

# extract the latent variables
X = torch.tensor(X, dtype=torch.float)
trained_autoencoder.eval()
_,latent = trained_autoencoder(X)

# train the MLP using the latent variables
ae_mlp_network = train(X=latent)

X.shape

from sklearn.metrics import average_precision_score
from sklearn.metrics import precision_recall_curve,f1_score, accuracy_score
from scipy import optimize

from copy import deepcopy
#Allow evaluation
if True:
  network = deepcopy(ae_mlp_network)
  network.eval()

  X,Y = torch.tensor(X, dtype=torch.float),torch.tensor(Y,dtype=torch.float)
  latent1 = latent.unsqueeze(1)

  #Get data for evaluating 
  Y_true = Y.detach().numpy()

  Y_scores = network(latent1)
  Y_scores = Y_scores.detach().numpy()
  # Y_scores =  [network(X1[i]).detach().numpy() for i in range(len(X1))]

else:
  network.eval()

  X,Y = torch.tensor(X, dtype=torch.float),torch.tensor(Y,dtype=torch.float)
  X1 = X.unsqueeze(1)

  #Get data for evaluating 
  Y_true = Y.detach().numpy()

  Y_scores = network(X1)
  Y_scores = Y_scores.detach().numpy()
  # Y_scores =  [network(X1[i]).detach().numpy() for i in range(len(X1))]

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

if True:
  #Get test data for evaluating 
  X_test = torch.tensor(X_test, dtype=torch.float)
  Y_test = torch.tensor(Y_test,dtype=torch.float)

  _,latent_test = trained_autoencoder(X_test)
  latent_test = latent_test.unsqueeze(1)

  Y_true_test = Y_test.detach().numpy()
  Y_scores_test = network(latent_test)
  Y_scores_test = Y_scores_test.detach().numpy()

  #Test data metric
  metric_func(Y_scores_test,Y_true_test, latent_test)

else:
  #Get test data for evaluating 
  X_test = torch.tensor(X_test, dtype=torch.float)
  Y_test = torch.tensor(Y_test,dtype=torch.float)

  Y_true_test = Y_test.detach().numpy()
  Y_scores_test =  [network(X_test[i]).detach().numpy() for i in range(len(X_test))]

  #Test data metric
  metric_func(Y_scores_test,Y_true_test, X_test)
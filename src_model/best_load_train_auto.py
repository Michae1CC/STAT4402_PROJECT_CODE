# -*- coding: utf-8 -*-
"""best_load_train_auto.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TJDTXJoL1Js5lj47TN7BZ4EpHRwfDjq0
"""

from tqdm import tqdm

import os
import numpy as np
    
import matplotlib.pyplot as plt

# Mount the STAT4402 drive to access feature space data and labels
from google.colab import drive
drive.mount('/content/drive')

lr	= 0.0005
auto_epoch_num = 100
epoch_num = 250
batch_size = 100	
HiddenLayer2Bool	= True
Unit1Layers	= 400
Unit2Layers	= 250
Unit3Layers = 0

latent_dim = 500
MS_ratio = 0.15
auto_lr = 0.0001
auto_epoch_num = 250
# auto_epoch_num = 10
auto_batch_size = 20

ms_latent_dim = round(MS_ratio * latent_dim)
ir_latent_dim = latent_dim - ms_latent_dim

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

x_data_path = os.path.join('/content/drive', 'My Drive', 'STAT4402_PROJECT', 'IR_MS_FUNCTIONAL_X_ALDE.npy')
y_data_path = os.path.join('/content/drive', 'My Drive', 'STAT4402_PROJECT', 'IR_MS_FUNCTIONAL_y_ALDE.npy')

X, X_test, Y, Y_test = load_project_data(x_data_path, y_data_path, train_size = 0.8)

# Split the training data into IR and MS groups
X_IR = X[:,:-500]
X_MS = X[:,-500:]

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
    self.hidden1 = nn.Sequential(nn.Linear(500, Unit1Layers), # 500 = no. latent variables
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



class Net3(nn.Module):

  global Unit1Layers
  global Unit2Layers
  global Unit3Layers

  def __init__(self):
    super(Net3,self).__init__()

    #layer 1
    self.hidden1 = nn.Sequential(nn.Linear(500, Unit1Layers), # 500 = no. latent variables
                               nn.ReLU())

    #layer 2
    self.hidden2 = nn.Sequential(nn.Linear(Unit1Layers,Unit2Layers),  
                               nn.ReLU())

    #layer 3
    self.hidden3 = nn.Sequential(nn.Linear(Unit2Layers,Unit3Layers),  
                               nn.ReLU())

    self.output = nn.Linear(Unit3Layers, Y.shape[1])

  def forward(self,x):
    x = self.hidden1(x)
    x = self.hidden2(x)
    x = self.hidden3(x)
    x = self.output(x)
    x = torch.sigmoid(x)
    return x

## Define an auto-encoder for IR only data
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

## Define an auto-encoder for MS only data
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

MLP_loss = []

def train(X ,
          Y = Y, 
          X_test = X_test,
          Y_test = Y_test,   
          loss_function=nn.BCELoss(),
          epoch_num = epoch_num,  
          batch_size= batch_size,
          lr=lr,
          HiddenLayer2Bool = HiddenLayer2Bool):
  
  mp_train, mp_test, f1_train, f1_test = [],[],[],[]

  X,Y = torch.tensor(X, dtype=torch.float),torch.tensor(Y,dtype=torch.float)

  if HiddenLayer2Bool:
    network = Net2()
  else:
    network = Net3()

  data_tuple = [[X[i], Y[i]] for i in range(len(X))] #accuracy 

  batch = torch.utils.data.DataLoader(data_tuple, 
                                      batch_size=batch_size, 
                                      shuffle=True)
  
  optimizer = optim.Adam(network.parameters(), 
                         lr=lr,
                         betas=(0.9, 0.999))

  for epoch in range(epoch_num):

    running_loss = 0

    for batch_shuffle in batch:
      
      x,y = batch_shuffle

      #Give loss
      optimizer.zero_grad()
      loss = loss_function(network(x),y)
      loss.backward()
      optimizer.step()

      running_loss += loss.item()
    if (epoch % 10 == 0) and (epoch > 0):
      mp_train1, mp_test1, f1_train1, f1_test1 = epoch_metric(network,
                                                              latent_all,
                                                              Y,
                                                              X_test,
                                                              Y_test)
      mp_train.append(mp_train1)
      mp_test.append(mp_test1)
      f1_train.append(f1_train1)
      f1_test.append(f1_test1)


    print("Iteration: ", epoch +1, ". Running loss: ", running_loss/batch_size)

    MLP_loss.append(running_loss/batch_size)

  return network, mp_train, mp_test, f1_train, f1_test

IR_save_path = os.path.join('/content/drive', 'My Drive', 'STAT4402_PROJECT', 'IR_network_dict.pkl')
MS_save_path = os.path.join('/content/drive', 'My Drive', 'STAT4402_PROJECT', 'MS_network_dict.pkl')

trained_autoencoder_IR = autoencode_IR()
# Load in the parameters dict from the pickled file
trained_autoencoder_IR.load_state_dict(torch.load(IR_save_path))
# Put the model in eval mode
trained_autoencoder_IR.eval()

trained_autoencoder_MS = autoencode_MS()
# Load in the parameters dict from the pickled file
trained_autoencoder_MS.load_state_dict(torch.load(MS_save_path))
# Put the model in eval mode
trained_autoencoder_MS.eval()

# make the X_IR and X_MS data into tensors
X_IR = torch.tensor(X_IR, dtype=torch.float)
X_MS = torch.tensor(X_MS, dtype=torch.float)
print(X_IR.shape)
print(X_MS.shape)

# then extract all the relevant latent variables
_,latentIR = trained_autoencoder_IR(X_IR)
_,latentMS = trained_autoencoder_MS(X_MS)
# combine both of these to create one feature vector of the new latent variables
latent_all = torch.cat((latentIR,latentMS),1)
latent_all.shape

from copy import deepcopy


def perfect_acc(cutoff, X = X, Y_scores = Y_scores, Y_true = Y_true):
  return -sum([np.array_equal(np.array(Y_scores[i] > cutoff, dtype=int), 
                              Y_true[i]) for i in range(len(X))]) /len(X)



def epoch_metric(net,X,Y,X_test,Y_test):

  global trained_autoencoder_IR, trained_autoencoder_MS

  mp_test, f1_test = 0,0
  #Allow evaluation
  network = deepcopy(net)
  network.eval()
  X = latent_all

  mp_train, mp_test, f1_train, f1_test = 0,0,0,0

  X,Y = torch.tensor(X, dtype=torch.float),torch.tensor(Y,dtype=torch.float)

  thres = [0.5 for _ in range(len(Y_test[0]))]

  #Get data for evaluating 
  Y_true = Y.detach().numpy()
  Y_scores =  [network(X[i]).detach().numpy() for i in range(len(X))]

  mp_train = -perfect_acc(thres,Y_scores = Y_scores, Y_true = Y_true, X=X)
  f1_train = f1_score(Y_true, [np.array(Y_scores[i] > thres, dtype=int) for i in range(len(Y_scores))],average = 'samples', zero_division = 0)

  # X_test_IR = X_test[:,:-500]
  X_test_IR = torch.tensor(X_test[:,:-500], dtype=torch.float)

  # X_test_MS = X_test[:,-500:]
  X_test_MS = torch.tensor(X_test[:,-500:], dtype=torch.float)

  print(X_test_IR.shape)
  print(X_test.shape)

  _,latent_test_IR = trained_autoencoder_IR(X_test_IR)
  # _,latent_test_MS = trained_autoencoder_MS(X_test_MS)
  # latent_test = torch.cat((latent_test_IR,latent_test_MS),1)
  # X_latent_test = latent_test
  # Y_test = torch.tensor(Y_test,dtype=torch.float)

  # print(Y_test.shape, X_latent_test.shape)

  # Y_true_test = Y_test.detach().numpy()
  # Y_scores_test =  [network(X_latent_test[i]).detach().numpy() for i in range(len(X_latent_test))]

  # mp_test = -perfect_acc(thres, Y_scores = Y_scores_test, Y_true = Y_true_test, X=X_latent_test)
  # f1_test = f1_score(Y_true_test, [np.array(Y_scores_test[i] > thres, dtype=int) for i in range(len(Y_scores_test))],average = 'samples', zero_division = 0)

  return mp_train, mp_test, f1_train, f1_test

# train the MLP using the latent variables
ae_mlp_network, mp_train, mp_test, f1_train, f1_test = train(X=latent_all)

#Molecular Perfection
x_plot = [10*i for i in range(1,int(epoch_num/10)) ]
fig, ax = plt.subplots()
plt.plot(x_plot ,mp_train, color='red')
plt.plot(x_plot ,mp_test, color='blue')
# plt.tick_params(
#     axis='x',          # changes apply to the x-axis
#     which='both',      # both major and minor ticks are affected
#     bottom=False,      # ticks along the bottom edge are off
#     top=False,         # ticks along the top edge are off
#     labelbottom=False)  # labels along the bottom edge are off
ax.set(xlabel='Epoch num', ylabel='Molecular Perfection',
       title='Epoch v Molecular Perfection')
ax.legend(['Train', 'Test'])

#F1 Score
fig, ax = plt.subplots()
plt.plot(x_plot ,f1_train, color='red')
plt.plot(x_plot ,f1_test, color='blue')
# plt.tick_params(
#     axis='x',          # changes apply to the x-axis
#     which='both',      # both major and minor ticks are affected
#     bottom=False,      # ticks along the bottom edge are off
#     top=False,         # ticks along the top edge are off
#     labelbottom=False)  # labels along the bottom edge are off
ax.set(xlabel='Epoch num', ylabel='F1 Score',
       title='Epoch v F1 Score')
ax.legend(['Train', 'Test'])

plt.plot(range(len(MLP_loss)), MLP_loss, color='red')
plt.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom=False,      # ticks along the bottom edge are off
    top=False,         # ticks along the top edge are off
    labelbottom=False)  # labels along the bottom edge are off
plt.title('MLP loss')
plt.xlabel('Epoch num')
plt.ylabel('Loss')
plt.show()

from sklearn.metrics import average_precision_score
from sklearn.metrics import precision_recall_curve,f1_score, accuracy_score
from scipy import optimize

#Allow evaluation
network = ae_mlp_network
network.eval()
X = latent_all

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
    thres_perf = optimal_thres_f1,
    thres_f1 = optimal_thres_f1):  #optimal_thres_f1
  
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
X, X_test, Y, Y_test = load_project_data(x_data_path, y_data_path, train_size = 0.8)
X_test = torch.tensor(X_test, dtype=torch.float)
X_test_IR = X_test[:,:-500]
X_test_MS = X_test[:,-500:]

_,latent_test_IR = trained_autoencoder_IR(X_test_IR)
_,latent_test_MS = trained_autoencoder_MS(X_test_MS)
latent_test = torch.cat((latent_test_IR,latent_test_MS),1)
X_test = latent_test
Y_test = torch.tensor(Y_test,dtype=torch.float)

Y_true_test = Y_test.detach().numpy()
Y_scores_test =  [network(X_test[i]).detach().numpy() for i in range(len(X_test))]

#Test data metric
metric_func(Y_scores_test,Y_true_test, X_test)

# Now do the lab data 
x_data_path_lab = os.path.join('/content/drive', 'My Drive', 'STAT4402_PROJECT', 'IR_MS_FUNCTIONAL_X_LAB.npy')
y_data_path_lab = os.path.join('/content/drive', 'My Drive', 'STAT4402_PROJECT', 'IR_MS_FUNCTIONAL_y_LAB.npy')

X_LAB = np.load(x_data_path_lab)
y_LAB = np.load(y_data_path_lab)

# Split the training data into IR and MS groups
X_LAB_IR = X_LAB[:,:-500]
X_LAB_MS = X_LAB[:,-500:]

#Get Lab data for evaluating
X_LAB_IR = torch.tensor(X_LAB_IR, dtype=torch.float)
X_LAB_MS = torch.tensor(X_LAB_MS, dtype=torch.float)
y_LAB = torch.tensor(y_LAB,dtype=torch.float)


# then extract all the relevant latent variables
_,latentIR = trained_autoencoder_IR(X_LAB_IR)
_,latentMS = trained_autoencoder_MS(X_LAB_MS)
# combine both of these to create one feature vector of the new latent variables
latent_LAB = torch.cat((latentIR,latentMS),1)


Y_true_lab = y_LAB.detach().numpy()
Y_scores_lab =  [network(latent_LAB[i]).detach().numpy() for i in range(len(latent_LAB))]

#Test data metric
metric_func(Y_scores_lab,Y_true_lab, X_LAB)

Y_scores_lab

X_test.shape

df_acc = pd.DataFrame({'Functional' :FUNC_GROUPS,
                   'Molecule 1 Predicted' : np.array(Y_scores_lab[0] > optimal_thres_f1, dtype=int),
                   'Molecule 1 True': Y_true_lab[0],
                    'Molecules 2 Predicted': np.array(Y_scores_lab[1] > optimal_thres_f1, dtype=int), 
                    'Molecules 2 True' : Y_true_lab[1],
                    'Molecule 3 Predicted': np.array(Y_scores_lab[2] > optimal_thres_f1, dtype=int),
                    'Molecule 3 True' : Y_true_lab[2],
                     'Molecule 4 Predicted':np.array(Y_scores_lab[3] > optimal_thres_f1, dtype=int),
                    'Molecule 4 True': Y_true_lab[3]})
print(tabulate(df_acc, headers='keys', tablefmt='psql'))
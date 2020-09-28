import os
from jcamp import JCAMP_reader
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle

with open('./data/IR_ABSORBANCE.pickle', 'rb') as handle:
    dc = pickle.load(handle)

datals = []
ls = []
for i in dc.keys():
    df = pd.DataFrame(list(zip(dc[i]['x'], dc[i]['y'])), columns=['x', i])
    df = df.groupby('x').aggregate(np.mean)
    df.reset_index(inplace=True)
    datals.append(df)
    ls.append([np.min(np.diff(df.x)), np.min(df.x), np.max(df.x)])
arr = np.array(ls)
bins = np.arange(np.min(arr[:, 1])-0.1,
                 np.max(arr[:, 2])+0.1, np.mean(arr[:, 0]))

datals[0]['x'] = pd.cut(datals[0]['x'], bins)
df = datals[0].groupby('x').aggregate(np.mean)
df.reset_index(inplace=True)

for i, df_ in enumerate(datals[1:]):
    df_['x'] = pd.cut(df_['x'], bins)
    df_ = df_.groupby('x').aggregate(np.mean)
    df_.reset_index(inplace=True)
    df = df.merge(df_, on='x', how='outer')
df.iloc[:, 1:] = df.iloc[:, 1:].interpolate(limit_direction='both', axis=0)
# df.to_csv("interpolateIR_TRANS.csv", index=False)
cas_idx = '50293'
print(df[cas_idx])
plt.bar(list(map(str, df.index)), list(df[cas_idx]))
plt.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom=False,      # ticks along the bottom edge are off
    top=False,         # ticks along the top edge are off
    labelbottom=False)  # labels along the bottom edge are off
plt.title(cas_idx)
plt.show()

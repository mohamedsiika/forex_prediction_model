# -*- coding: utf-8 -*-
"""GP_Preprocessing_Data.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1v2crFkaB7z9JwkqMX_qqomgyPxvIZ5J9
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
import keras
from keras import layers
import tensorflow as tf
import pickle

df = pd.read_excel('data_Hourly.xlsx')
df.drop('Unnamed: 0', inplace=True, axis=1)
df.drop(['real_volume','spread'], inplace=True, axis=1)
df.head()

df['HLAvg'] = df['high'].add(df['low']).div(2)
df.head()

df['MA'] = df['HLAvg'].rolling(window=14).mean()    # We chose 14 as this is the default period used in most technical analysis tools
            # Because the window = 14 ... the first 13 row in MA will be NaN and then they will have a value .. So we may delete them
df

df['Returns'] = np.log(df['MA']/df['MA'].shift(1))
df

df=df.dropna()

df=df.reset_index()
df=df.drop("index",axis=1)

"""#Batch size"""

batch_size=32
reminder=df.shape[0]%batch_size
print(reminder)
df=df.drop(df.index[:reminder])
df

df=df.reset_index()
df=df.drop("index",axis=1)
df=df.set_index("time")
df

from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
df["scaled_return"]= scaler.fit_transform(df[['Returns']].values)

pickle.dump(scaler,open("scaler.bin",'wb'))

df

df.to_excel("final_df.xlsx")

features=df.drop(["open","high","low","HLAvg","MA","Returns","close","tick_volume"],axis=1)

train_size=int((0.8*df.shape[0])-((0.8*df.shape[0])% batch_size))
print(train_size)
test_size=(df.shape[0]-train_size)//2
print(test_size)

val_size=(df.shape[0]-train_size)//2
print(val_size)

window_size=2*batch_size #64 hours
df_train = features[:- val_size - test_size]
df_val = features[- val_size - test_size - window_size:- test_size]
df_test = features[- test_size - window_size:]

df_test

def features_labels1(values):
  x,y=[],[]
  for i in range(window_size, len(values)):
        x.append(values[i-window_size:i])
        y.append(values[i])

  x=np.array(x)
  y=np.array(y)
  x = np.reshape(x, (x.shape[0], x.shape[1], 1))

  return x,y

def features_labels2(df):
  x,y=[],[]
  for i in range(df.shape[0]-window_size-1):
    x.append(np.array(df[i:i+window_size]))
    y.append(features['scaled_return'].iloc[i+window_size])
    

  x=np.array(x)
  y=np.array(y)
  return x,y

x_train,y_train=features_labels1(features[['scaled_return']].values)
x_val,y_val=features_labels1(df_val[['scaled_return']].values)

x_train.shape

model = keras.models.Sequential()
model.add(layers.LSTM(76, input_shape=(x_train.shape[1], 1), return_sequences = False))
model.add(layers.Dropout(0.2))
model.add(layers.Dense(1))
model.compile(loss="mse", optimizer='Adam')
model.summary()

model.fit(x=x_train, y=y_train ,epochs=50,batch_size=32,validation_data=(x_val,y_val),shuffle=False)

y_pred=model.predict(x_train)

len(np.unique(y_pred))/len(y_pred)

filename = 'finalized_model.sav'
pickle.dump(model, open(filename, 'wb'))

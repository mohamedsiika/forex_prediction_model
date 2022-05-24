import pandas as pd
import pickle
import numpy as np
import tensorflow
import pandas as pd
EURUSD_1hour_MA_scaler = pickle.load(open("scaler.bin",'rb'))

def scaledReturn_MA(df,MA_windowSize = 14):
    # add conditions to know which scaler to use
    df.drop(['real_volume', 'spread','open','close','tick_volume'], inplace=True, axis=1)
    df['HLAvg'] = df['high'].add(df['low']).div(2)
    df['MA'] = df['HLAvg'].rolling(window = MA_windowSize).mean()
    df['Returns'] = np.log(df['MA'] / df['MA'].shift(1))
    df = df.dropna()
    df = df.reset_index()
    df = df.drop("index", axis=1)
    df["scaled_return"] = EURUSD_1hour_MA_scaler.fit_transform(df[['Returns']].values)

    finaldf = df.drop(['high','low'],inplace=True, axis=1)
    final = df['scaled_return'].values
    last_MA = df['MA'].iloc[-1]
    return final,last_MA

def scaledReturn_to_MA(prediction,lastMA):
    #add conditions to know which scaler to use
    unscaled = EURUSD_1hour_MA_scaler.inverse_transform(prediction)
    MA_pred = []
    MA_pred.append(np.exp(unscaled[0])*lastMA)
    for i in range(1,len(prediction)):
        MA_pred.append(np.exp(unscaled[i]) * MA_pred[i-1])
    return MA_pred


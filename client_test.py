import MetaTrader5 as mt5
import numpy as np
import time
import pandas as pd
import DataPreprocessing_funs
mt5.initialize()
def get_data():
    
    return df



prices = pd.DataFrame(mt5.copy_rates_from_pos('EURUSD', mt5.TIMEFRAME_H1, 0, 78))
_, _, prices = DataPreprocessing_funs.scaledReturn_MA(prices)
prices.dropna(inplace=True)
prices = prices[['close', 'HLAvg', 'MA', "tick_volume", 'scaled_return']].values
new_price=prices[-1]

try:
    client_info=pd.read_csv('client_info.csv')
    flag=1
    header=False
except:
    flag=0
    positions = np.array([[2] for i in range(64)])
    profit = np.array([[0] for i in range(64)])
    header=True

if flag==1:
    positions = client_info['position'].iloc[-63:]
    profit = client_info['profit'].iloc[-63:]

    position_opened=mt5.positions_get()
    if len(position_opened)==0:
        current_pos=2
        current_profit=0
    else:
        current_pos=position_opened[0].type
        current_profit=position_opened[0].profit




    positions=np.array(positions).reshape(63,1)
    positions=np.append(positions,[1]).reshape(64,1)

    profit=np.array(profit).reshape(63,1)
    profit=np.append(profit,[1]).reshape(64,1)
    print(profit)



t = np.concatenate((prices, positions, profit), axis=1)

df=pd.DataFrame(data=t,columns=['close','HLAvg', 'MA', "tick_volume", 'scaled_return','position','profit'],dtype=float)
print(df.head())
df.to_csv('client_info.csv',index=False,mode='a',header=header)


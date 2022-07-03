from trader_DQN import trader
from environment import OhlcvEnv
import pandas as pd

df=pd.read_excel('./data/test/data_Hourly.xlsx')
z=df[:10]

trader=trader()
model=trader.dqn.load_weights('./model/duel_dqn_OHLCV-v0_weights_1101LS_211_200_98.73.h5f')

env_test=OhlcvEnv(window_size=10,test_data=df)
info=model.test(env_test,nb_episodes=1)
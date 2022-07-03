from trader_DQN import trader
from environment import OhlcvEnv
import pandas as pd


class Predict():
    def __init__(self):
        self.trader=trader()
        self.model=self.trader.dqn.load_weights('./model/duel_dqn_OHLCV-v0_weights_1152LS_0_74_155.06000000000066.h5f')



    def action(self,df):
        self.df = df
        self.env_test = OhlcvEnv(window_size=64, test_data=self.df)
        self.info=self.model.test(self.env_test,nb_episodes=1)
        return self.info['history']





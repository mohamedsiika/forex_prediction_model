from trader_DQN import trader
from environment import OhlcvEnv
import pandas as pd


class Predict():
    def __init__(self):
        self.trader=trader()
        self.trader.dqn.load_weights('./model/duel_dqn.h5f')



    def action(self,df):
        self.df = df
        self.env_test = OhlcvEnv(window_size=64, test_data=self.df)
        self.info=self.trader.dqn.test(self.env_test,nb_episodes=1)
        return self.info['history']

if __name__ == '__main__':
    df = pd.read_csv('df.csv')
    pred=Predict()
    print(pred.action(df))





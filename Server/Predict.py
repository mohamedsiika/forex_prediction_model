import numpy as np
from trader_DQN import trader
from DataPreprocessing_funs import DataPreprocessing


class Predict():
    def __init__(self):
        self.trader = trader()
        self.trader.dqn.load_weights('duel_dqn.h5f')

    def action(self, df):
        dataf = DataPreprocessing()
        self.df = df
        _, _, self.df = dataf.scaledReturn_MA(self.df)
        self.df['positions'] = self.df['positions'].astype(int)
        temp = self.df['positions'].apply(lambda x: np.eye(3)[x])
        encoder_positions = []
        for i in range(64):
            encoder_positions.append(temp.values[i])

        profit = self.df['profit'].values.reshape(64, 1)
        encoder_positions = np.array(encoder_positions)
        prices = self.df[['close', 'HLAvg', 'MA', "tick_volume", 'scaled_return']].values
        prices = np.concatenate((prices, encoder_positions, profit), axis=1)
        action = self.trader.dqn.model.predict(np.array([prices]))

        return np.argmax(action)

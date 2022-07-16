from MA_action_funs import *
import pickle
import keras


class DataPreprocessing():
    def __init__(self):
        self.EURUSD_1hour_MA_scaler = pickle.load(open("scaler_H1.bin", 'rb'))
        self.EURUSD_1hour_MA_model = keras.models.load_model("HL_MovingAvg_H1_model.sav")

    def scaledReturn_MA(self, df, MA_windowSize=14):
        # add conditions to know which scaler to use-
        df.drop(['real_volume', 'spread', 'open'], inplace=True, axis=1)
        df['HLAvg'] = df['high'].add(df['low']).div(2)
        df['MA'] = df['HLAvg'].rolling(window=MA_windowSize).mean()
        df['Returns'] = np.log(df['MA'] / df['MA'].shift(1))
        df = df.dropna()
        df = df.reset_index()
        df = df.drop("index", axis=1)
        df["scaled_return"] = self.EURUSD_1hour_MA_scaler.fit_transform(df[['Returns']].values)

        finaldf = df
        finaldf.drop(['high', 'low'], inplace=True, axis=1)
        final = df['scaled_return'].values
        last_MA = df['MA'].iloc[-1]
        finaldf = self.add_change(finaldf, last_MA)
        return final, last_MA, finaldf

    def scaledReturn_to_MA(self, prediction, lastMA):
        # add conditions to know which scaler to use
        unscaled = self.EURUSD_1hour_MA_scaler.inverse_transform(prediction)
        MA_pred = []
        MA_pred.append(np.exp(unscaled[0]) * lastMA)
        for i in range(1, len(prediction)):
            MA_pred.append(np.exp(unscaled[i]) * MA_pred[i - 1])
        return MA_pred

    def add_change(self, df, lastMA):
        val = df['scaled_return'].values
        x = self.features(val)
        changeCol = []
        for i in range(len(x)):
            pred = self.EURUSD_1hour_MA_predict(x[i], self.EURUSD_1hour_MA_model)
            ma = self.scaledReturn_to_MA(pred, lastMA)
            changeCol.append(get_change(ma))

        df = df.drop(df.index[:63])
        df['change'] = changeCol
        return df

    def features(self, values):
        x = []
        if (len(values) > 63):
            for i in range(64, len(values) + 1):
                x.append(values[i - 64:i])
        else:
            x.append(values)

        x = np.array(x)
        x = np.reshape(x, (x.shape[0], x.shape[1]))

        return x

    def MultiStep(self, test, window_size, steps=1):
        y_pred = []
        step_pred = 0
        len = 0
        window_pred = []
        if (test.shape == (window_size,)):  # to handle whether one window or several
            window = test
            len = 1
        else:
            window = test[0]
            len = test.shape[0]

        for j in range(len):
            for i in range(steps):
                window = np.reshape(window, (1, window_size, 1))
                step_pred = self.EURUSD_1hour_MA_model.predict(window)
                window_pred.append(step_pred)
                window = np.delete(window, 0)
                window = np.append(window, step_pred)
            y_pred.append(window_pred)
            window_pred = []
        y_pred = np.array(y_pred)
        y_pred = np.reshape(y_pred, (steps, len))
        return y_pred

    def EURUSD_1hour_MA_predict(self, window, model):
        return self.MultiStep(window, 64, 10)

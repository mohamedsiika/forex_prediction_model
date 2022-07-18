import datetime as dt
import keras
from DataPreprocessing_funs import DataPreprocessing
import pickle
import numpy as np


class Model_Retrain():
    def __init__(self):
        self.EURUSD_1hour_MA_model = keras.models.load_model("finalized_model.sav")
        self.features_windowSize = 64
        self.now = dt.datetime.now()

        self.updatingDataNeeded = dict()
        self.last = dict()

        self.lastUpdated = pickle.load(open('lastUpdated_dates', 'rb'))

    def off_days(self, d1, d2):
        # Monday = 0,...., Sunday = 6
        daysNumbers = []
        day = d1.weekday()
        daysNumbers.append(day)
        for i in range((d2 - d1).days - 1):
            day += 1
            daysNumbers.append(day % 7)
        days = daysNumbers.count(5) + daysNumbers.count(6)
        return days

    def days_diff(self, d1, d2):
        diff = (d2 - d1) + dt.timedelta(1 / 12)  # to calculate difference in hours accuratly
        diff = diff.total_seconds() // (60 * 60 * 24)
        diff -= self.off_days(d1, d2)

        return diff

    def check_update(self):
        # difference in days for each timeframe without considering days off (sundays,mondays)
        hour_diff = self.days_diff(self.lastUpdated['H1'], self.now)
        # min30_diff = self.days_diff(self.lastUpdated['M30'], self.now)
        # min10_diff = self.days_diff(self.lastUpdated['M10'], self.now)

        if (hour_diff > 14):  # last update is more than 15 days ago
            self.updatingDataNeeded['H1'] = int(hour_diff * 24) + 14  # for the MA window in the model
        else:
            self.updatingDataNeeded['H1'] = 0

        # if (min30_diff > 4):  # last update is more than 5 days ago
        #     self.updatingDataNeeded['M30'] = int(min30_diff * 24 * 2) + 14  # for the MA window in the model
        # else:
        #     self.updatingDataNeeded['M30'] = 0
        #
        # if (min10_diff > 1):  # last update is more than 2 days ago
        #     self.updatingDataNeeded['M10'] = int(min10_diff * 24 * 6) + 14  # for the MA window in the model
        # else:
        #     self.updatingDataNeeded['M10'] = 0

    def update_is_needed(self):
        for i in self.updatingDataNeeded.values():
            if i != 0:
                return True
        return False

    def update_models(self, data):
        dp = DataPreprocessing()
        features, _, _ = dp.scaledReturn_MA(data)
        x, y = self.features_labels(features)
        self.EURUSD_1hour_MA_model.fit(x, y)
        keras.models.save_model(self.EURUSD_1hour_MA_model, "finalized_model.sav")
        pickle.dump(self.lastUpdated, open("lastUpdated_dates", 'wb'))

    def features_labels(self, values):
        x, y = [], []
        for i in range(self.features_windowSize, len(values)):
            x.append(values[i - self.features_windowSize:i])
            y.append(values[i])

        x = np.array(x)
        y = np.array(y)
        x = np.reshape(x, (x.shape[0], x.shape[1], 1))
        return x, y

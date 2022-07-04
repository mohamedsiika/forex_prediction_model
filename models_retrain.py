import datetime as dt
import pickle

from DataPreprocessing_funs import *
from models_predictions import *
features_windowSize = 64
now = dt.datetime.now()

updatingDataNeeded = dict()
last = dict()

lastUpdated = pickle.load(open('lastUpdated_dates','rb'))

print(lastUpdated)
def off_days(d1, d2):
  # Monday = 0,...., Sunday = 6
  daysNumbers = []
  day = d1.weekday()
  daysNumbers.append(day)
  for i in range((d2-d1).days-1):
    day+=1
    daysNumbers.append(day%7)
  days = daysNumbers.count(0)+daysNumbers.count(6)
  return days

def days_diff(d1,d2):
  diff = (d2-d1)+dt.timedelta(1/12)   # to calculate difference in hours accuratly
  diff = diff.total_seconds()//(60*60*24)
  diff -= off_days(d1,d2)

  return diff

def check_update():
  # difference in days for each timeframe without considering days off (sundays,mondays)
  hour_diff = days_diff(lastUpdated['H1'],now)
  min30_diff = days_diff(lastUpdated['M30'],now)
  min10_diff = days_diff(lastUpdated['M10'],now)

  print(hour_diff)
  print(min30_diff)
  print(min10_diff)

  if(hour_diff > 14):                                       # last update is more than 15 days ago
    updatingDataNeeded['H1'] = int(hour_diff*24) + 14             # for the MA window in the model
  else:
    updatingDataNeeded['H1'] = 0

  if(min30_diff > 4 ):                                       # last update is more than 5 days ago
    updatingDataNeeded['M30'] = int(min30_diff*24*2) + 14             # for the MA window in the model
  else:
    updatingDataNeeded['M30'] = 0

  if(min10_diff > 1):                                       # last update is more than 2 days ago
    updatingDataNeeded['M10'] = int(min10_diff*24*6) + 14             # for the MA window in the model
  else:
    updatingDataNeeded['M10'] = 0


def UpdateIsNeeded():
  for i in updatingDataNeeded.values():
    if(i != 0):
      return True
  return False




print(lastUpdated)
print(updatingDataNeeded)
check_update()
def update_models(data):
  print(" >>> Models are being updated ...")
  features,_= scaledReturn_MA(data)
  print(features)
  print(len(features))
  x,y = features_labels(features)
  print(x,y)
  print("x shape :",x.shape)
  print("y shape: ",y.shape)
  #EURUSD_1hour_MA_model.fit(x,y)
  tf.keras.models.save_model(EURUSD_1hour_MA_model,"finalized_model.sav")
  #lastUpdated['H1'] = dt.datetime.now()
  #pickle.dump(lastUpdated,open("lastUpdated_dates",'wb'))



def features_labels(values):
  x,y=[],[]
  for i in range(features_windowSize, len(values)):
        x.append(values[i-features_windowSize:i])
        y.append(values[i])

  x=np.array(x)
  y=np.array(y)
  x = np.reshape(x, (x.shape[0], x.shape[1], 1))

  return x,y
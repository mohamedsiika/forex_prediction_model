import pickle
import numpy as np
import tensorflow as tf
import keras

EURUSD_1hour_MA_model = tf.keras.models.load_model("finalized_model.sav")



def MultiStep(test,model,window_size,steps = 1):
  y_pred = []
  step_pred = 0
  len = 0
  window_pred = []

  if(test.shape == (window_size,1)):      # to handle whether one window or several
    window = test
    len = 1
  else:
    window = test[0]
    len = test.shape[0]

  for j in range( len ):
    for i in range(steps):
      window = np.reshape(window,(1,window_size,1))
      step_pred = model.predict(window)
      window_pred.append(step_pred)
      window = np.delete(window,0)
      window = np.append(window,step_pred)
    y_pred.append(window_pred)
    window_pred = []
  y_pred = np.array(y_pred)
  y_pred = np.reshape(y_pred,(len,steps))
  return y_pred

def EURUSD_1hour_MA_predict(window,model):
   MultiStep(window, model,10)

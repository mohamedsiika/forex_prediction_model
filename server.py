

import socket
import threading
from models_predictions import *
from DataPreprocessing_funs import *

port=5050
SERVER=socket.gethostbyname(socket.gethostname()) #gets the ip server
ADDR=(SERVER,port)

server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server.bind(ADDR)
FORMAT="utf-8"
HEADER=64

DISCONNECT_MSG='!DISCONNECTED'

def predict_MA_direction(msg,DataNature=None):
    # add conditions for DataNature to specify the model
    window,lastma = scaledReturn_MA(msg)
    pred_MA = EURUSD_1hour_MA_predict(window,EURUSD_1hour_MA_model)# Predict scaled return
    pred_MA = scaledReturn_to_MA(pred_MA,lastma)          # Convert it back to MA
    '''
        Here we got the predicted Moving Average values
        Now we get the direction of these values
    '''
    return pred_MA

def handle_client(conn,addr):
    connected=True
    while connected:
        msg=pickle.loads(conn.recv(10000))

        '''
            add another msg (DataNature),conditions to know the nature of the data
            to use the appropriate model 
        '''
        msg=pd.DataFrame(msg)
        ma=predict_MA_direction(msg)
        print('predict_moving=',ma)
    conn.close()

def start():
    server.listen()
    while True:
        conn,addr=server.accept()
        thread=threading.Thread(target=handle_client,args=(conn,addr))
        thread.start()
print("server is starting")

start()



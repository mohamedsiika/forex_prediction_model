import pandas as pd
import matplotlib.pyplot as plt
import socket
import threading
from MA_action_funs import *
from models_retrain import *


port=7070
SERVER=socket.gethostbyname(socket.gethostname()) #gets the ip server
ADDR=(SERVER,port)

server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server.bind(ADDR)
FORMAT="utf-8"
HEADER=64

DISCONNECT_MSG='!DISCONNECTED'

def predict_MA_direction(msg,DataNature=None):
    # add conditions for DataNature to specify the model
    window,lastma= scaledReturn_MA(msg)
    pred_MA = EURUSD_1hour_MA_predict(window,EURUSD_1hour_MA_model)# Predict scaled return
    pred_MA = scaledReturn_to_MA(pred_MA,lastma)          # Convert it back to MA
    '''
        Here we got the predicted Moving Average values
        Now we get the direction of these values
    '''
    print(pred_MA)
    plt.plot(pred_MA, color='red', label='Predicted', alpha=0.5)

    plt.show()

    change=get_change(pred_MA)
    return change

def handle_client(conn,addr):
    connected=True
    while connected:
        msg=pickle.loads(conn.recv(10000))
        msg=pd.DataFrame(msg)
        thereIs = 0
        check_update()
        if(UpdateIsNeeded()):
            thereIs = 1
            print(" >>> Models are out of date ! ")
            conn.send(str(thereIs).encode())
            conn.send(str(updatingDataNeeded).encode())
            UpdatingData = pickle.loads(conn.recv(1000000))
            UpdatingData = pd.DataFrame(UpdatingData)
            print(UpdatingData)
            update_models(UpdatingData)
            print(" >>> Models are updated successfully. ")
        else:
            conn.send(str(thereIs).encode())
        change=str(predict_MA_direction(msg)).encode()
        print('predict_moving=',change)
        conn.send(change)
        connected=False

    conn.close()

def start():
    server.listen()
    while True:
        conn,addr=server.accept()
        thread=threading.Thread(target=handle_client,args=(conn,addr))
        thread.start()
print("server is starting")

start()



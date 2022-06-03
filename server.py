
import matplotlib.pyplot as plt
import socket
import threading
from models_predictions import *
from DataPreprocessing_funs import *
from MA_action_funs import *



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
        change=str(predict_MA_direction(msg)).encode()
        print('predict_moving=',change)
        conn.send(change)
        connected=False

    print("out")
    conn.close()

def start():
    server.listen()
    while True:
        conn,addr=server.accept()
        thread=threading.Thread(target=handle_client,args=(conn,addr))
        thread.start()
print("server is starting")

start()



import pickle
import socket
import MetaTrader5 as mt5
import pandas as pd
from MA_action_funs import *
from DataPreprocessing_funs import *
import matplotlib.pyplot as plt

def initialize_meta(accountID,passwrd,ser):
    start = mt5.initialize(login=accountID, password=passwrd, server=ser)
    print("started")
    if not start:
        print("not started")
        print("initialize() failed, error code =", mt5.last_error())
        quit()


def account_login(accountID,passwrd,ser):
    authorized = mt5.login(login=accountID, password=passwrd, server=ser)
    print("in login")
    if authorized:
        # display trading account data 'as is'
        print(mt5.account_info())
        # display trading account data in the form of a list
        print("Show account_info()._asdict():")
        account_info_dict = mt5.account_info()._asdict()

        return authorized

    else:
        print("failed to connect at account #{}, error code: {}".format(accountID, mt5.last_error()))
        return None

def get_data():

    df = pd.DataFrame(mt5.copy_rates_from_pos('EURUSD', mt5.TIMEFRAME_H1, 0, 78))
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df


account_id = 65353266
account_pass = "Miro@forex5"
server = "XMGlobal-MT5 2"
print("before start")
initialize_meta(account_id,account_pass,server)
print("after start")


df = get_data()
print(df)


FORMAT = "utf-8"
HEADER = 64
DISCONNECT_MSG = '!DISCONNECTED'
port = 7070
IP = socket.gethostbyname(socket.gethostname())  # gets the ip server
ADDR = (IP, port)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def updating_models_data(req):
    data = []
    for key in req.keys():
        print(key)
        if req[key] != 0:

            if key == 'H1':
                df = pd.DataFrame(mt5.copy_rates_from_pos('EURUSD', mt5.TIMEFRAME_H1, 0, req[key]))
                df['time'] = pd.to_datetime(df['time'], unit='s')
                return df
        """
            if key == 'M30':
                df = pd.DataFrame(mt5.copy_rates_from_pos('EURUSD', mt5.TIMEFRAME_M30, 0, req[key]))
                df['time'] = pd.to_datetime(df['time'], unit='s')
                data.append(df)
            if key == 'M10':
                df = pd.DataFrame(mt5.copy_rates_from_pos('EURUSD', mt5.TIMEFRAME_M10, 0, req[key]))
                df['time'] = pd.to_datetime(df['time'], unit='s')
                data.append(df)
        """
    return data

def send_msg(msg):
    message = msg
    client.send(message)
    Updating = client.recv(1000)
    Updating = Updating.decode()
    Updating = bool(int(Updating))
    if Updating :
        print("Models are being updated ... ")
        required = client.recv(1000)
        required = eval(required.decode())          # risky conversion to read the dict
        print(required)
        data = updating_models_data(required)
        print(data)
        client.send(pickle.dumps(data, protocol=4))
    else:
        print("all good")
    msg=client.recv(1000)
    while msg:
        print('Received:' + msg.decode())
        trade,sl,tp=Action(1.06993,msg)
        print(trade)
        if trade!="no_action":
            if trade=="buy":
                trade_type=mt5.ORDER_TYPE_BUY
            else:
                trade_type=mt5.ORDER_TYPE_SELL

            buy_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": "EURUSD",
                "volume": 0.1,
                "type": trade_type,
                "price": 1.06993,
                "sl": sl,
                "tp": tp,
                "comment": "sent by python",

            }

            result = mt5.order_send(buy_request)
            print(result)
            print(sl,tp)


        msg = client.recv(1024)


send_msg(pickle.dumps(df,protocol=4))

import pickle
import socket
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pytz
import pandas as pd

mt5.Sell()
def initialize_meta():
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        quit()


def get_data():
    # timezone = pytz.timezone('ETC/UTC')
    # now = datetime.now()
    # from_date = datetime.now() - timedelta(hours=78)
    # print(now)
    # print(from_date)

    df = pd.DataFrame(mt5.copy_rates_from_pos('EURUSD', mt5.TIMEFRAME_H1, 0, 78))
    df['time'] = pd.to_datetime(df['time'], unit='s')

    return df


def account_login(accountID):
    authorized = mt5.login(login=accountID, password="dezjrca7", server="MetaQuotes-Demo")
    if authorized:
        # display trading account data 'as is'
        print(mt5.account_info())
        # display trading account data in the form of a list
        print("Show account_info()._asdict():")
        account_info_dict = mt5.account_info()._asdict()

        return authorized

    else:
        print("failed to connect at account #{}, error code: {}".format(account, mt5.last_error()))
        return None


account_id = 59238033
initialize_meta()
df = get_data()
account = account_login(account_id)

print(df)


FORMAT = "utf-8"
HEADER = 64
DISCONNECT_MSG = '!DISCONNECTED'
port = 5050
IP = socket.gethostbyname(socket.gethostname())  # gets the ip server
ADDR = (IP, port)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def send_msg(msg):
    message = msg
    client.send(message)


send_msg(pickle.dumps(df,protocol=4))

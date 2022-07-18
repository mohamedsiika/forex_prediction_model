import sys
import MetaTrader5 as mt5
import pandas as pd
import requests
import numpy as np
from streamlit import cli as stlci
import schedule

import time
import threading
import os
from dashboard import *


def initialize_meta():
    if not mt5.initialize():
        print("initialize() failed, error code = ", mt5.last_error())
        quit()


def get_data():
    global positions, profit
    df = pd.DataFrame(mt5.copy_rates_from_pos('EURUSD', mt5.TIMEFRAME_H1, 0, 141))
    df['time'] = pd.to_datetime(df['time'], unit='s')
    try:
        client_info = pd.read_csv('client_info.csv')
        flag = 1
        header = False
    except:
        flag = 0
        positions = np.array([[2] for i in range(141)])
        positions = np.array(positions).reshape(141, 1)

        profit = np.array([[0] for i in range(141)])
        profit = np.array(profit).reshape(141, 1)

        header = True

    if flag == 1:
        temp = pd.DataFrame(mt5.copy_rates_from_pos('EURUSD', mt5.TIMEFRAME_H1, 0, 1))
        temp = temp.values
        position_opened = mt5.positions_get()
        if len(position_opened) == 0:
            current_pos = 2
            current_profit = 0
        else:
            current_pos = position_opened[0].type
            current_profit = position_opened[0].profit

        data = np.concatenate((temp, np.array([[current_pos]]), np.array([[current_profit]])), axis=1)

    else:
        # print(df.values.shape, positions.shape, profit.shape)
        data = np.concatenate((df.values, positions, profit), axis=1)

    dataframe = pd.DataFrame(data=data, columns=['time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread',
                                                 'real_volume', 'positions', 'profit'])

    dataframe.to_csv('client_info.csv', index=False, mode='a', header=header)


def account_login(accountID=59238033, password="dezjrca7"):
    global id, passw
    id = accountID
    passw = password
    authorized = mt5.login(login=accountID, password=password, server="MetaQuotes-Demo")
    if authorized:
        # print(mt5.account_info())
        # print("Show account_info()._asdict():")
        return authorized
    else:
        print("failed to connect at account #{}, error code: {}".format(account, mt5.last_error()))
        return None


initialize_meta()
account = account_login()


def updating_models_data(req):
    data = []
    for key in req.keys():
        print(key)
        if req[key] != 0:

            if key == 'H1':
                df = pd.DataFrame(mt5.copy_rates_from_pos('EURUSD', mt5.TIMEFRAME_H1, 0, req[key]))
                df['time'] = pd.to_datetime(df['time'], unit='s')
                return df
    return data


def trade():
    get_data()
    df = pd.read_csv('client_info.csv')
    df = df.iloc[-141:]
    dataset = df.to_dict(orient='list')
    post_data = {'df': dataset}
    # post_data_url = "https://forex-app-fudn2.ondigitalocean.app/getAction"
    post_data_url = "http://127.0.0.1:5000/getAction"
    r_action = requests.post(post_data_url, json=post_data, stream=True)
    response_action = r_action.json()
    action = response_action['Response']['Action']

    if action == "0":
        if len(mt5.positions_get()) == 0:
            trade_type = mt5.ORDER_TYPE_BUY
            buy_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": "EURUSD",
                "volume": 0.01,
                "type": trade_type,
                "price":mt5.symbol_info_tick('EURUSD').ask,
                "comment": "sent by Barter",
            }
            result=mt5.order_send(buy_request)

            print("BUY")

        elif mt5.positions_get()[0].type == 1:
            trade_type = mt5.ORDER_TYPE_BUY
            buy_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": "EURUSD",
                "volume": 0.01,
                "type": trade_type,
                "price": mt5.symbol_info_tick('EURUSD').ask,

                "comment": "sent by Barter",
                "position": mt5.positions_get()[0].ticket
            }
            result=mt5.order_send(buy_request)
            print("SELL CLOSE")




    elif action == "1":
        if len(mt5.positions_get()) == 0:
            trade_type = mt5.ORDER_TYPE_SELL
            buy_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": "EURUSD",
                "volume": 0.01,
                "type": trade_type,
                "price": mt5.symbol_info_tick('EURUSD').bid,

                "comment": "sent by Barter",
            }
            result=mt5.order_send(buy_request)
            print("BUY")

        elif mt5.positions_get()[0].type == 0:
            trade_type = mt5.ORDER_TYPE_SELL
            buy_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": "EURUSD",
                "volume": 0.01,
                "type": trade_type,
                "price":mt5.symbol_info_tick('EURUSD').bid,
                "comment": "sent by Barter",
                "position": mt5.positions_get()[0].ticket
            }
            result=mt5.order_send(buy_request)
            print("BUY CLOSE")

    else:
        print("HOLD")
    print(result)


    # get_update_need_url = "https://forex-app-fudn2.ondigitalocean.app/dataUpdate"
    get_update_need_url = "http://127.0.0.1:5000/dataUpdate"
    r_updates = requests.get(get_update_need_url)
    response_updates = r_updates.json()
    print(response_updates['Response']['Dict'])
    if response_updates['Response']['Dict'] != "False":
        updated_data = updating_models_data(dict(response_updates['Response']['Dict']))
        # print("update data", '\n', updated_data)
        updated_data['time'] = updated_data['time'].astype(str)

        dataset = updated_data.to_dict(orient='list')
        post_data = {'df': dataset}
        # update_models_url = "https://forex-app-fudn2.ondigitalocean.app/updateModels"
        update_models_url = "http://127.0.0.1:5000/updateModels"
        r_update_models = requests.post(update_models_url, json=post_data)
        response_update_models = r_update_models.json()
        # print(response_update_models)


def trade_every_hour():
    schedule.every(1).hours.do(trade)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    trade()
    thread = threading.Thread(target=trade_every_hour)
    thread.start()
    os.system('cmd /c "streamlit run dashboard.py"')

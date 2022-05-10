import MetaTrader5 as mt5
import datetime
import time
import pickle
import pytz
import pandas as pd

mt5.initialize()


def live():
    # set the time zone
    timezone = pytz.timezone('ETC/UTC')
    # set the date we wants to get the datafrom
    from_date = datetime.datetime(2012, 1, 1, 0, 0, 0, tzinfo=timezone)
    # set the live time
    now = datetime.datetime.now()
    print(now)
    to_date = datetime.datetime(2022, 4, 22, 0, 0, 0, tzinfo=timezone)
    # create the dataframe

    df_monthly = pd.DataFrame(mt5.copy_rates_range('EURUSD', mt5.TIMEFRAME_MN1, from_date, to_date))
    df_monthly['time'] = pd.to_datetime(df_monthly['time'], unit='s')

    df_weekly = pd.DataFrame(mt5.copy_rates_range('EURUSD', mt5.TIMEFRAME_W1, from_date, to_date))
    df_weekly['time'] = pd.to_datetime(df_weekly['time'], unit='s')

    df_dialy = pd.DataFrame(mt5.copy_rates_range('EURUSD', mt5.TIMEFRAME_D1, from_date, to_date))
    df_dialy['time'] = pd.to_datetime(df_dialy['time'], unit='s')

    print(df_monthly.columns)
    df_monthly.to_excel('data_monthly.xlsx')

    df_weekly.to_excel('data_weekly.xlsx')

    df_dialy.to_excel('data_dialy.xlsx')
    # time.sleep(60)


live()

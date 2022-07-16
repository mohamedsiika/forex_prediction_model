import MetaTrader5 as mt5
from datetime import datetime

import plotly.express as px
import pandas as pd
import streamlit as st

import numpy as np
from streamlit_option_menu import option_menu


# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ", mt5.__author__)
print("MetaTrader5 package version: ", mt5.__version__)

# establish MetaTrader 5 connection to a specified trading account
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

account_info=mt5.account_info()
balance=account_info.balance
login=account_info.login
equity=account_info.equity
print(balance)


# get the number of deals in history
from_date=datetime(2020,1,1)
to_date=datetime.now()

deals=mt5.history_deals_get(from_date, to_date)
deals=list(deals)
for i in deals:
    if i.profit==0:
        deals.remove(i)

deals_number=len(deals)

num_current_pos=mt5.positions_total()
pos = mt5.positions_get()
# for open cuurent orders

positions=pd.DataFrame(list(pos),columns=pos[0]._asdict().keys())
positions['time'] = pd.to_datetime(positions['time'], unit='s')
opendf = positions.loc[:, ['profit']]
opendf = opendf.iloc[0: , :]

positions=positions.drop(columns=['ticket','time_msc','time_update_msc','time_update','sl','tp','swap','external_id','magic'])

# for trade history deals

deals=pd.DataFrame(list(deals),columns=deals[0]._asdict().keys())
deals['time'] = pd.to_datetime(deals['time'], unit='s')
df = deals.loc[:, ['profit']]
df = df.iloc[1: , :]
deals = deals.iloc[1: , :]

print(df)

deals=deals.drop(columns=['ticket','swap','external_id','magic','commission','fee','reason','position_id','order'])



with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",  # required
        options=["Home", "Tarde History Deals", "Current Deals"], # required
        icons=["house", "bar-chart-line", "activity"],  # optional
        menu_icon="cast",  # optional
        default_index=0,  # optional
                )


show_positions=st.sidebar.checkbox(label="show current positions")
if show_positions:
    st.title("Positions")
    st.write(positions)

show_deals=st.sidebar.checkbox(label="show deals history")
if show_deals:
    st.title("history")
    st.write(deals)


if selected == "Home":
    st.title(f" {selected}")
    st.write(f'This is your  Login number {login}')
    st.write(f'This is your  Current balance {balance}')
    st.write(f'This is your  Current Equity {equity}')
if selected == "Tarde History Deals":
    st.title(f" {selected}")
    st.write(f'This is your Total number of deals {deals_number}')
    # st.bar_chart(df3)
    st.line_chart(df)


if selected == "Current Deals":
    st.title(f" {selected}")
    st.write(f'Number of current open trades {num_current_pos}')
    plot2 = px.bar(data_frame=opendf, x=opendf.index, y=opendf['profit'],width=500)
    st.plotly_chart(plot2)

    #st.line_chart(opendf)
    # if pos  ==None:
    #     print("No positions ".format(mt5.last_error()))
    #     st.write(f'Number of current open order {num_current_order}')
    #     st.write(f'Number of current open trades {num_current_pos}')
    #
    # elif len(pos) > 0:
    #     print("positions_get".format(len(pos)))
    #     # display these positions as a table using pandas.DataFrame
    #     opendf = pd.DataFrame(list(pos), columns=pos[0]._asdict().keys())
    #     opendf['time'] = pd.to_datetime(opendf['time'], unit='s')
    #     opendf = opendf.loc[:, ['profit']]
    #     opendf = opendf.iloc[1:, :]
    #     st.line_chart(opendf)

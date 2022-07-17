import MetaTrader5 as mt5
from datetime import datetime

import plotly.express as px
import pandas as pd
import streamlit as st

import numpy as np
from streamlit_option_menu import option_menu
from streamlit import cli as stlci
import sys
import re


def initialize_meta():
    if not mt5.initialize():
        print("initialize() failed, error code = ", mt5.last_error())
        quit()


initialize_meta()

account_info = mt5.account_info()
balance = account_info.balance
login = account_info.login
equity = account_info.equity


def main():
    # get the number of deals in history
    from_date = datetime(2020, 1, 1)
    to_date = datetime.now()

    deals = mt5.history_deals_get(from_date, to_date)
    deals = list(deals)
    for i in deals:
        if i.profit == 0:
            deals.remove(i)

    deals_number = len(deals)

    num_current_pos = mt5.positions_total()
    pos = mt5.positions_get()
    # for open cuurent orders

    if len(pos) > 0:
        positions = pd.DataFrame(list(pos), columns=pos[0]._asdict().keys())
        positions['time'] = pd.to_datetime(positions['time'], unit='s')
        opendf = positions.loc[:, ['profit']]
        opendf = opendf.iloc[0:, :]

        positions = positions.drop(
            columns=['ticket', 'time_msc', 'time_update_msc', 'time_update', 'sl', 'tp', 'swap', 'external_id',
                     'magic'])

    # for trade history deals

    deals = pd.DataFrame(list(deals), columns=deals[0]._asdict().keys())
    deals['time'] = pd.to_datetime(deals['time'], unit='s')
    df = deals.loc[:, ['profit']]
    df = df.iloc[1:, :]
    deals = deals.iloc[1:, :]

    deals = deals.drop(
        columns=['ticket', 'swap', 'external_id', 'magic', 'commission', 'fee', 'reason', 'position_id', 'order'])

    with st.sidebar:
        selected = option_menu(
            menu_title="Main Menu",  # required
            options=["Home", "Tarde History Deals", "Current Deals"],  # required
            icons=["house", "bar-chart-line", "activity"],  # optional
            menu_icon="cast",  # optional
            default_index=0,  # optional
        )

    show_positions = st.sidebar.checkbox(label="show current positions")
    if show_positions:
        st.title("Positions")
        st.write(positions)

    show_deals = st.sidebar.checkbox(label="show deals history")
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
        if len(pos) > 0:
            plot2 = px.bar(data_frame=opendf, x=opendf.index, y=opendf['profit'], width=500)
            st.plotly_chart(plot2)


if __name__ == '__main__':
    main()

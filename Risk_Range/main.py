import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import datetime
import threading
import time

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.ticktype import TickTypeEnum

import rescaled_range as rs


fmt = '%.0f%%'
yticks = ticker.FormatStrFormatter(fmt)
# Ticker = 'SPY'
Pair = 'GBP'

def sma(lst, timeperiod):
    return lst.rolling(timeperiod).mean()

def getting_datetime():
    '''
    :return: Gets the date of today and if it's weekend it returns the date of the previous friday (because Financial markets don't trade in the weekend).
    '''
    current_time = datetime.datetime.now()
    last_friday = (current_time.date()
                   - datetime.timedelta(days=current_time.weekday())
                   + datetime.timedelta(days=4))
    last_friday_at_21 = datetime.datetime.combine(
        last_friday, datetime.time(20,59,59))
    if True:
        today = last_friday_at_21
        df_string = today.strftime("%Y%m%d %H:%M:%S")
        return df_string
    else:
        return datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")

def get_data(Ticker):
    '''
    :param Ticker: Security Symbol/Ticker
    :return: Dataframe with Closing prices and Date of security
    '''
    ticker_list = pd.read_csv('../data/tickers/export.csv').set_index('Ticker')
    contract = Contract()
    if not Ticker in list(ticker_list.index):
        print('Ticker not in list')

    elif ticker_list.loc[Ticker][0] == 'STK':
        contract.secType = ticker_list.loc[Ticker][0]
        contract.exchange = ticker_list.loc[Ticker][1]
        contract.currency = 'USD'
        contract.symbol = Ticker
        app.reqHistoricalData(1, contract, getting_datetime(), '1 Y', '1 day', 'MIDPOINT', 0, 1, False, [])

    # elif ticker_list.loc[Ticker][0] == 'FUT':
    #     contract.secType = ticker_list.loc[Ticker][0]
    #     contract.exchange = ticker_list.loc[Ticker][1]
    #     contract.currency = 'USD'
    #     contract.lastTradeDateOrContractMonth = ticker_list.loc[Ticker][2]
    #     contract.multiplier = ticker_list.loc[Ticker][3]
    #     contract.symbol = Ticker
    #     app.reqHistoricalData(1, contract, getting_datetime(), '1 Y', '1 day', 'MIDPOINT', 0, 1, False, [])

    # elif ticker_list.loc[Ticker][0] == 'CASH':
    #     contract.secType = ticker_list.loc[Ticker][0]
    #     contract.exchange = ticker_list.loc[Ticker][1]
    #     contract.currency = Pair
    #     contract.symbol = Ticker

    time.sleep(1)
    data = pd.DataFrame(app.data, columns=['DateTime', 'Close'])
    data['DateTime'] = pd.to_datetime(data['DateTime'], format='%Y%m%d')
    return data, contract.symbol

def get_chart(data):
    '''
    :param data: Dataframe from get_data() function
    :return: Plots a graph and a moving average of the security' closing prices
    '''
    x = data[0]['DateTime']
    y = data[0]['Close']
    ticker = data[1]

    fig, ax = plt.subplots()
    ax.plot(x,y)
    ax.plot(x, y.rolling(25).mean())
    ax.set_title('{}'.format(ticker))
    return fig



# def streamlit():
#     '''
#     :return: Makes the layout of the Streamlit Application
#     '''
#     st.title('{} Trend Tracker'.format('SPY'))
#     st.pyplot(get_chart(get_data('SPY')))
#     st.pyplot(rs.hurst(get_data('SPY')['Close']))
#     # st.dataframe(corr_table())

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = []

    def historicalData(self, reqId, bar):
        self.data.append([bar.date, bar.close])

def run_loop():
    app.run()

app = IBapi()
app.connect('127.0.0.1', 7496, clientId='0')

# Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()
time.sleep(1)  # Sleep interval to allow time for connection to server.

# print(get_chart(get_data('MSFT')))
print(corr_table())


if __name__ == '__main__':
    # streamlit()
    app.disconnect()

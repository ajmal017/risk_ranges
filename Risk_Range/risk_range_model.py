#!/usr/bin/env python3

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.ticktype import TickTypeEnum

import threading
import time
import datetime
import pandas as pd
import numpy as np
import scipy.stats as si
import sympy as sy
from sympy.stats import Normal, cdf
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from matplotlib.ticker import Formatter


class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = []

    def historicalData(self, reqId, bar):
        #print(f'Time: {bar.date} Close: {bar.close}')
        self.data.append([bar.date, bar.close])


def run_loop():
    app.run()


app = IBapi()
app.connect('127.0.0.1', 7496, 123)

# Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1)  # Sleep interval to allow time for connection to server.

# Create contract object
apple_contract = Contract()
apple_contract.symbol = 'AAPL'
apple_contract.secType = 'STK'
apple_contract.exchange = 'SMART'
apple_contract.currency = 'USD'

Ticker = apple_contract.symbol

Quotes_dir = {}

def getting_datetime():
    weekend_days = [5, 6]
    week_days = [0, 1, 2, 3, 4]
    current_weekday = datetime.datetime.today().weekday()
    current_time = datetime.datetime.now()
    last_friday = (current_time.date()
                   - datetime.timedelta(days=current_time.weekday())
                   + datetime.timedelta(days=4))
    last_friday_at_21 = datetime.datetime.combine(
        last_friday, datetime.time(21))
    df_string = ''
    if current_weekday in weekend_days:
        today = last_friday_at_21
        df_string = today.strftime("%d%m%Y %H:%M:%S")
    elif current_weekday in week_days:
        today = datetime.datetime.now()
        df_string = today.strftime("%Y%m%d %H:%M:%S")
    return df_string


# Request historical candles
app.reqHistoricalData(1, apple_contract, getting_datetime(),
                      '1 Y', '1 day', 'MIDPOINT', 0, 1, False, [])

# Request Market Data
# app.reqMktData(1, apple_contract, '', True, True, [])

time.sleep(2)
app.disconnect()

df = pd.DataFrame(app.data, columns=['DateTime', 'Close'])
df['DateTime'] = pd.to_datetime(df['DateTime'], format='%Y%m%d')
N = len(df.DateTime)
ind = np.arange(N)

#spot price
S = df['Close'].iloc[-1]
#print(S)

#strike price
K = df['Close'].iloc[-1].round()  
#print(K)

#time to maturity
#T = 

##interest rate
#r =  
#
##volatility of underlying asset
#sigma = 

# format date
def format_date(x, pos=None):
    thisind = np.clip(int(x + 0.5), 0, N - 1)
    return df.DateTime[thisind].strftime('%Y-%m-%d')

# getting hurst component of ticker
def hurst(ts):
    ts = list(ts)
    N = len(ts)
    if N < 20:
        raise ValueError(
            "Time series is too short! input series ought to have at least 20 samples!")
    max_k = int(np.floor(N / 2))
    R_S_dict = []
    for k in range(10, max_k + 1):
        R, S = 0, 0
        # split ts into subsets
        subset_list = [ts[i:i + k] for i in range(0, N, k)]
        # print(subset_list)
    if np.mod(N, k) > 0:
        subset_list.pop()
        # tail = subset_list.pop()
    # subset_list[-1].extend(tail)
    # calc mean of every subset
    mean_list = [np.mean(x) for x in subset_list]
    for i in range(len(subset_list)):
        cumsum_list = pd.Series(subset_list[i] - mean_list[i]).cumsum()
        R += max(cumsum_list) - min(cumsum_list)
        S += np.std(subset_list[i])
        R_S_dict.append({"R": R / len(subset_list),
                         "S": S / len(subset_list), "n": k})

    log_R_S = []
    log_n = []
    print(R_S_dict)
    for i in range(len(R_S_dict)):
        R_S = (R_S_dict[i]["R"] + np.spacing(1)) / \
            (R_S_dict[i]["S"] + np.spacing(1))
        log_R_S.append(np.log(R_S))
        log_n.append(np.log(R_S_dict[i]["n"]))

    Hurst_exponent = np.polyfit(log_n, log_R_S, 1)[0]
    return Hurst_exponent


# getting average true range
def avg_true_range(lst, timeperiod):
	pass

# getting simple moving averages
def sma(lst, timeperiod):
    return lst.rolling(timeperiod).mean()

# getting exponential moving averages
def ema(lst, timeperiod):
	return lst.ewm(span=timeperiod).mean()

# getting realised volatility
# This calculation is probably wrong so I have to change it later on. 
def realised_vol(lst, timeperiod):
	log_returns = np.log(lst/lst.shift(1))
	return log_returns.rolling(window=timeperiod).std() * np.sqrt(timeperiod)	

# getting implied volatility
def implied_vol(lst, timeperiod):
	pass

# getting expected_range
def expected_range(lst, timeperiod):
    pass

def realised_range(lst, timeperiod):
    pass

#print(sma(df.Close, 10))


def fmt_xaxes(ax):
	ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
	
fig,(ax1, ax2) = plt.subplots(ncols=2, figsize=(15,10))
fig.autofmt_xdate()
ax1.plot(ind, df['Close'], '-')
ax1.plot(sma(df['Close'], 10))
ax1.plot(sma(df['Close'], 60))
ax1.plot(sma(df['Close'], 30))
ax1.plot(ema(df['Close'], 10))
ax1.plot(ema(df['Close'], 30))
ax1.plot(ema(df['Close'], 60))
fmt_xaxes(ax1)

ax2.plot(realised_vol(df['Close'], 30))
fmt_xaxes(ax2)

plt.title(Ticker)
plt.tight_layout()
plt.show()






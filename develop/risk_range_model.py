#!/usr/bin/env python

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.ticktype import TickTypeEnum
from plotly.subplots import make_subplots


import threading
import dash
import dash_core_components as dcc
import dash_html_components as html
import time
import math
import datetime
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import seaborn as sns
import scipy.stats as si
import sympy as sy
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import relative_performance as rp

from sympy.stats import Normal, cdf
from matplotlib.ticker import Formatter
from dash.dependencies import Input, Output, State

# btc = pd.read_csv('./data/BTC-USD.csv')
# spy = pd.read_csv('./data/SPY.csv')
# gc = pd.read_csv('./data/GLD.csv')
# eurusd = pd.read_csv('./data/DX=F.csv')
# vix = pd.read_csv('./data/^VIX.csv')
# tnx = pd.read_csv('./data/^TNX.csv')
# input = pd.read_csv('./data/SLV.csv')

def getting_datetime():
    weekend_days = [5, 6]
    week_days = [0, 1, 2, 3, 4]
    current_weekday = datetime.datetime.today().weekday()
    current_time = datetime.datetime.now()
    last_friday = (current_time.date()
                   - datetime.timedelta(days=current_time.weekday())
                   + datetime.timedelta(days=4))
    last_friday_at_21 = datetime.datetime.combine(
        last_friday, datetime.time(20,59,59))
    df_string = ''
    #if current_weekday in weekend_days:
    if True:
        today = last_friday_at_21
        df_string = today.strftime("%Y%m%d %H:%M:%S")
        return df_string
    else:
        return datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")

N = 240
ind = np.arange(N)
df_year = None

def parkinson_vol(df_year, N, window=11, clean=True):
    rs = (1.0 / (4.0 * math.log(2.0))) * ((df_year['High'] / df_year['Low']).apply(np.log))**2.0
    def f(v):
        return N * v.mean()**0.5
    result = rs.rolling(window=window, center=False).apply(func=f)
    if clean:
        return result
    else:
        return result

def garman_klass_vol(price_data, N, window=11, clean=True):
    log_hl = (price_data['High'] / price_data['Low']).apply(np.log)
    log_co = (price_data['Close'] / price_data['Open']).apply(np.log)
    rs = 0.5 * (log_hl**2) - (2*math.log(2)-1) * (log_co**2)

    def f(v):
        return(N * v.mean())**0.5

    result = rs.rolling(window=window, center=False).apply(func=f)

    if clean:
        return result
    else:
        return result

def gk_yang_zhang_vol(price_data, N, window=30, clean=True):
    log_ho = (price_data['High'] / price_data['Open']).apply(np.log)
    log_lo = (price_data['Low'] / price_data['Open']).apply(np.log)
    log_co = (price_data['Close'] / price_data['Open']).apply(np.log)
    
    log_oc = (price_data['Open'] / price_data['Close'].shift(1)).apply(np.log)
    log_oc_sq = log_oc**2
    
    log_cc = (price_data['Open'] / price_data['Close'].shift(1)).apply(np.log)
    log_cc_sq = log_cc**2

    rs = log_ho * (log_ho - log_co) + log_lo * (log_lo - log_co)
    
    close_vol = log_cc_sq.rolling(window=window, center=False).sum() * (1.0 / (window - 1.0))
    open_vol = log_oc_sq.rolling(window=window, center=False).sum() * (1.0 / (window - 1.0))
    window_rs = rs.rolling(window=window, center=False).sum() * (1.0 / (window - 1.0))

    k = 0.34 / (1 + (window + 1) / (window -1))
    result = (open_vol + k * close_vol + (1-k) * window_rs).apply(np.sqrt) * math.sqrt(N)

    if clean:
        return result
    else:
        return result

# format date
def format_date(x, pos=None):
    thisind = np.clip(int(x + 0.5), 0, N - 1)
    global df_year
    return df_year['DateTime'][thisind].strftime('%Y-%m-%d')

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
    #print(R_S_dict)
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
    return lst['Close'].rolling(timeperiod).mean()

# getting exponential moving averages
def ema(lst, timeperiod):
    return lst['Close'].ewm(span=timeperiod).mean()

# getting realised volatility
# This calculation is probably wrong so I have to change it later on. 
def realised_vol(lst, timeperiod):
    log_returns = np.log(lst['Close']/lst['Close'].shift(1))
    return log_returns.rolling(window=timeperiod).std() * np.sqrt(timeperiod)

fmt = '%.0f%%' 
yticks = ticker.FormatStrFormatter(fmt)

def fmt_xaxes(ax):
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))


#setup api connection with Dash
appdash = dash.Dash(__name__)

#dash layout
appdash.layout = html.Div(style={"font-family":"verdana"}, children=[
    html.H1("Volatily Analyzer", style={'text-align': 'center'}),
    
    html.Div(id="inputs", style={"textAlign":"center"}, children=[
        html.Div(className="ticker_info", children=[
            dcc.Input(id="Ticker", value='', placeholder="Input Ticker please")]),
        
        html.Br(),
        html.Button("letsgo", id='button')]),

    html.Div(id='outputs', children=[
        dcc.Graph(id='my_output1'),
        dcc.Graph(id='my_output2')
    ])
])

@appdash.callback(
    Output(component_id="my_output1", component_property='figure'),
    Input("button", 'n_clicks'),
    state=[State("Ticker", "value")]
)
def get_chart(button, Ticker):
    global df_year

    contract = Contract()
    contract.secType = 'STK'
    contract.exchange = 'SMART'
    contract.currency = 'USD'
    contract.symbol = Ticker

    app.reqHistoricalData(1, contract, getting_datetime(), '2 Y', '1 day', 'MIDPOINT', 0, 1, False, [])
    time.sleep(2)

    df = pd.DataFrame(app.data, columns=['DateTime', 'Close', 'High', 'Low', 'Open'])
    df['DateTime'] = pd.to_datetime(df['DateTime'], format='%Y%m%d')
    df_year = df[:N]

    df_sma = sma(df_year, 50).to_frame().fillna(1)
    x = np.arange(0, len(df_year))

    fig = make_subplots(rows=1, cols=2)
    fig.append_trace(go.Scatter(x=x, y=df_year["Close"]), row=1, col=1)
    fig.append_trace(go.Scatter(x=x, y=df_sma["Close"]), row=1, col=1)
    fig['layout'].update(height=600, width=3000, title=f'{contract.symbol} - Chart')
    return fig

@appdash.callback(
    Output(component_id="my_output2", component_property='figure'),
    Input("button", 'n_clicks'),
    state=[State("Ticker", "value")]
)
def get_corr_chart(button, Ticker):
    contract_ticker = Contract()
    contract_ticker.secType = 'STK'
    contract_ticker.exchange = 'SMART'
    contract_ticker.currency = 'USD'
    contract_ticker.symbol = Ticker
    input_df = app.reqHistoricalData(2, contract_ticker, getting_datetime(), '2 Y', '1 day', 'MIDPOINT', 0, 1, False, [])

    contract_btc = Contract()
    contract_btc.secType = 'FUT'
    contract_btc.exchange = 'CMECRYPTO'
    contract_btc.currency = 'USD'
    contract_btc.symbol = 'BTCG1'
    btc_df = app.reqHistoricalData(3, contract_btc, getting_datetime(), '2 Y', '1 day', 'MIDPOINT', 0, 1, False, [])

    contract_spy = Contract()
    contract_spy.secType = 'IND'
    contract_spy.exchange = 'CBOE'
    contract_spy.currency = 'USD'
    contract_spy.symbol = 'SPX'
    spx_df = app.reqHistoricalData(4, contract_spy, getting_datetime(), '2 Y', '1 day', 'MIDPOINT', 0, 1, False, [])

    contract_usd = Contract()
    contract_usd.secType = 'STK'
    contract_usd.exchange = 'SMART'
    contract_usd.currency = 'USD'
    contract_usd.symbol = 'UUP'
    uup_df = app.reqHistoricalData(5, contract_usd, getting_datetime(), '2 Y', '1 day', 'MIDPOINT', 0, 1, False, [])

    contract_gold = Contract()
    contract_gold.secType = 'STK'
    contract_gold.exchange = 'SMART'
    contract_gold.currency = 'USD'
    contract_gold.symbol = 'GLD'
    gld_df = app.reqHistoricalData(6, contract_gold, getting_datetime(), '2 Y', '1 day', 'MIDPOINT', 0, 1, False, [])

    contract_vix = Contract()
    contract_vix.secType = 'IND'
    contract_vix.exchange = 'CBOE'
    contract_vix.currency = 'USD'
    contract_vix.symbol = 'VIX'
    vix_df = app.reqHistoricalData(7, contract_vix, getting_datetime(), '2 Y', '1 day', 'MIDPOINT', 0, 1, False, [])

    contract_tnx = Contract()
    contract_tnx.secType = 'IND'
    contract_tnx.exchange = 'CBOE'
    contract_tnx.currency = 'USD'
    contract_tnx.symbol = 'TNX'
    tnx_df = app.reqHistoricalData(8, contract_btc, getting_datetime(), '2 Y', '1 day', 'MIDPOINT', 0, 1, False, [])

    time.sleep(2)

    input = pd.DataFrame(input_df, columns=['Date', 'Close'])
    btc = pd.DataFrame(btc_df, columns=['Date', 'Close'])
    spx = pd.DataFrame(spx_df, columns=['Date', 'Close'])
    usd = pd.DataFrame(uup_df, columns=['Date', 'Close'])
    gold = pd.DataFrame(gld_df, columns=['Date', 'Close'])
    vix = pd.DataFrame(vix_df, columns=['Date', 'Close'])
    tnx = pd.DataFrame(tnx_df, columns=['Date', 'Close'])
    return rolling_bitcoin_correlation_graph_30d(rp.get_correlation_table(input, btc, gold, usd, spx, vix, tnx))

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = []

    def historicalData(self, reqId, bar):
        #print(f'Time: {bar.date} Close: {bar.close}')
        self.data.append([bar.date, bar.close, bar.high, bar.low, bar.open])

def run_loop():
    app.run()

app = IBapi()
app.connect('127.0.0.1', 7496, clientId='0')

# Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1)  # Sleep interval to allow time for connection to server.

if __name__ == '__main__':
    appdash.run_server(debug=False)
    app.disconnect()



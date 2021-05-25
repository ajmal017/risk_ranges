import pandas as pd
import numpy as np
import plotly.graph_objects as go

from datetime import datetime
from dateutil.relativedelta import relativedelta
from dash_project.get_data import all_tickers_data
from hurst import compute_Hc
from sklearn.linear_model import LinearRegression


def hurst(TICKER):
    data = all_tickers_data.loc[:,f'{TICKER}_close']
    log_returns = np.log(data) - np.log(data.shift(1))
    ts = list(log_returns[2:])
    N = len(ts)
    if N < 10:
        raise ValueError("Time series is too short! input series ought to have at least 20 samples!")
    max_k = int(np.floor(N / 2))
    R_S_dict = []
    for k in range(2, max_k + 1):
        R, S = 0, 0
        # split ts into subsets
        subset_list = [ts[i:i + k] for i in range(0, N, k)]
        if np.mod(N, k) > 0:
            subset_list.pop()
        mean_list = [np.mean(x) for x in subset_list]
        for i in range(len(subset_list)):
            cumsum_list = pd.Series(subset_list[i] - mean_list[i]).cumsum()
            R += max(cumsum_list) - min(cumsum_list)
            S += np.std(subset_list[i])
        R_S_dict.append({"R": R / len(subset_list), "S": S / len(subset_list), "n": k})
    log_R_S = []
    log_n = []
    for i in range(len(R_S_dict)):
        R_S = (R_S_dict[i]["R"] + np.spacing(1)) / (R_S_dict[i]["S"] + np.spacing(1))
        log_R_S.append(np.log(R_S))
        log_n.append(np.log(R_S_dict[i]["n"]))

    x = np.array(log_n)
    y = np.array(log_R_S)
    return x, y

def hurst_regression_fig(data):
    x, y = data
    fig = go.Figure(go.Scatter(
        x=x,
        y=y
    ))
    lr = LinearRegression()
    lr.fit(x.reshape(len(x), 1), y)
    return fig

def calc_hurst(data):
    log_returns = np.log(data) - np.log(data.shift(1))
    ts = list(log_returns[2:])
    N = len(ts)
    if N < 10:
        raise ValueError("Time series is too short! input series ought to have at least 20 samples!")
    max_k = int(np.floor(N / 2))
    R_S_dict = []
    for k in range(2, max_k + 1):
        R, S = 0, 0
        # split ts into subsets
        subset_list = [ts[i:i + k] for i in range(0, N, k)]
        if np.mod(N, k) > 0:
            subset_list.pop()
        mean_list = [np.mean(x) for x in subset_list]
        for i in range(len(subset_list)):
            cumsum_list = pd.Series(subset_list[i] - mean_list[i]).cumsum()
            R += max(cumsum_list) - min(cumsum_list)
            S += np.std(subset_list[i])
        R_S_dict.append({"R": R / len(subset_list), "S": S / len(subset_list), "n": k})
    log_R_S = []
    log_n = []
    for i in range(len(R_S_dict)):
        R_S = (R_S_dict[i]["R"] + np.spacing(1)) / (R_S_dict[i]["S"] + np.spacing(1))
        log_R_S.append(np.log(R_S))
        log_n.append(np.log(R_S_dict[i]["n"]))
    x = np.array(log_n)
    y = np.array(log_R_S)
    lr = LinearRegression()
    lr.fit(x.reshape(len(x), 1), y)
    hurst = list(lr.coef_)
    intercept = lr.intercept_
    return hurst, intercept

def hurst_cyle_graph(TICKER):
    data = all_tickers_data[TICKER+'_close']
    range_n = [21, 63, 126, 251]
    hurst_n = []
    for n in range_n:
        hurst_n.append(calc_hurst(data[-n:])[0])
    len_hurst_n = len(hurst_n)
    x = np.array(np.arange(len_hurst_n))
    y = np.hstack(hurst_n)
    fig = go.Figure(go.Scatter(
        x=x,
        y=y
    ))
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=np.array(np.arange(len_hurst_n)),
            ticktext=" ".join([str(i) for i in range_n]).split()
        )
    )
    return fig

def realised_vol(TICKER):
    window_size = 30
    data = all_tickers_data[TICKER + '_close']
    vol_30d = data.pct_change().rolling(window_size).std() * (252 ** 0.5)
    vol_30d = vol_30d[30:]
    return vol_30d

def realised_vol_graph(data):
    weeks = []
    for i in range(0,len(data)):
        weeks.append(datetime.now() - relativedelta(days=i))
    weeks.reverse()
    fig = go.Figure(go.Scatter(
        x=weeks,
        y=data,
        name='30d realised vol'
    ))
    fig.update_layout(yaxis_tickformat='%')
    return fig




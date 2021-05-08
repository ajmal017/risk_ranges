import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import dash_bootstrap_components as dbc

from datetime import timedelta, date
from dash.dependencies import Input, Output, State
from dash_project.get_data import all_tickers_data
from .server import app


@app.callback(
    Output('corr_table_window_x', 'children'),
    [Input('input_on_submit', 'value'),
     Input('submit_val_rel_p', 'n_clicks')],
    [State('input_on_submit_rel_p', 'value')]
)
def get_correlation_table_window_x(TICKER, n_clicks, MULTP_TICKERS):
    '''
    :return: Correlation table of the securities
    '''
    MULTP_TICKERS = [i + '_close' for i in MULTP_TICKERS]
    data = all_tickers_data.loc[:,MULTP_TICKERS]
    ticker_data = all_tickers_data.loc[:,f'{TICKER}_close']
    ticker_data_log_ret = np.log(ticker_data) - np.log(ticker_data.shift(1))

    dataframe = pd.DataFrame()
    window_list = [15, 30, 90, 120]
    for window in window_list:
        for i in list(MULTP_TICKERS):
            data_log_ret = np.log(data[i])-np.log(data[i].shift(1))
            dataframe[f'{TICKER}_{i}_{window}'] = ticker_data_log_ret.rolling(window).corr(data_log_ret)
    l = int(len(dataframe.columns)/len(window_list))
    day_15 = dataframe.iloc[:,:l].dropna()
    day_30 = dataframe.iloc[:, l:l*2].dropna()
    day_90 = dataframe.iloc[:,l*2:l*3].dropna()
    day_120 = dataframe.iloc[:,l*3:l*4].dropna()
    rolling_30d_max = [dataframe[i].max() for i in list(day_30.columns)]
    rolling_30d_min = [dataframe[i].min() for i in list(day_30.columns)]

    df = pd.DataFrame()
    df['15D'] = np.array(day_15.iloc[-1,:])
    df['30D'] = np.array(day_30.iloc[-1,:])
    df['90D'] = np.array(day_90.iloc[-1,:])
    df['120D'] = np.array(day_120.iloc[-1,:])
    df['1y 30d high'] = rolling_30d_max
    df['1y 30d low'] = rolling_30d_min
    MULTP_TICKERS = [i[:-6] for i in MULTP_TICKERS]
    df.index = MULTP_TICKERS
    df = df.reset_index().rename(columns={'index':'vs'}).round(2)
    return dbc.Table.from_dataframe(df, bordered=True)

@app.callback(
    Output('performance_table', 'children'),
    [Input('submit_val', 'n_clicks'),
     Input('submit_val_rel_p', 'n_clicks')],
    [State('input_on_submit', 'value'),
     State('input_on_submit_rel_p', 'value')]
)
def get_performance(n_clicks, n_clicks_rel_val, TICKER, MULTP_TICKERS):
    window_names = ['ticker','daily','weekly','monthly','quarterly','yearly', 'vs 52w max', 'vs 52w min']
    df = pd.DataFrame()
    MULTP_TICKERS = [i + '_close' for i in MULTP_TICKERS]
    ticker_list = [f'{TICKER}_close'] + MULTP_TICKERS
    for ticker in ticker_list:
        data = all_tickers_data[ticker]
        latest = data[-1]
        range = [2, 6, 21, 63, 252]
        results = []
        for time in range:
            results.append((latest - data[-time]) / latest)
        yearly_high = data.max()
        yearly_low = data.min()
        vs_52_max = -((yearly_high - latest) / latest)
        vs_52_min = -((yearly_low - latest) / latest)
        results.append(vs_52_max)
        results.append(vs_52_min)
        results = ["{:.2%}".format(y) for y in results]
        df[ticker[:-6]] = results
    df = df.T.reset_index()
    df.columns = window_names
    return dbc.Table.from_dataframe(df.round(2), bordered=True)

@app.callback(
    Output('relative_p', 'children'),
    [Input('input_on_submit', 'value'),
     Input('submit_val_rel_p', 'n_clicks')],
    [State('input_on_submit_rel_p', 'value')]
)
def relative_performance(TICKER, n_clicks, MULTP_TICKERS):
    window_names_rel_performance = ['vs', 'daily', 'weekly', 'monthly', 'quarterly', 'yearly']
    MULTP_TICKERS = [i + '_close' for i in MULTP_TICKERS]
    data = all_tickers_data.loc[:,MULTP_TICKERS]
    ticker_data = all_tickers_data.loc[:,f'{TICKER}_close']
    df = pd.DataFrame()
    range = [2, 6, 21, 63, 252]
    for i in MULTP_TICKERS:
        results = []
        latest_i = data[i].iloc[-1]
        latest_td = ticker_data[-1]
        for time in range:
            results.append(((latest_td - ticker_data[-time]) / latest_td) - ((latest_i - data[i].iloc[-time]) / latest_i))
        results = ["{:.2%}".format(y) for y in results]
        df[i[:-6]] = results
    df = df.T.reset_index()
    df.columns = window_names_rel_performance
    return dbc.Table.from_dataframe(df, bordered=True)


def factor_sector_performance():
    window_names = ['index','1D','1W','1M','3M','6M','YTD']
    df = pd.DataFrame()
    ticker_list = ['HYG','SPHQ','SPHB','USMV']

    start_dt = date(2021, 1, 1)
    end_dt = date.today()
    len_ytd = 0
    weekdays = [5,6]
    for dt in daterange(start_dt, end_dt):
        if dt.weekday() not in weekdays:
            len_ytd += 1

    for ticker in ticker_list:
        data = all_tickers_data[ticker+'_close']
        latest = data[-1]
        range = [2, 6, 21, 63, 126, len_ytd]
        results = []
        for time in range:
            results.append((latest - data[-time]) / latest)
        results = ["{:.2%}".format(y) for y in results]
        df[ticker] = results
    df = df.T.reset_index()
    df.columns = window_names
    df['Factor'] = ['High yield','Low yield', 'High beta', 'Low beta']
    return dbc.Table.from_dataframe(df.round(2), bordered=True)

def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)












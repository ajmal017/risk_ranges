import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
from dash_project.get_data import all_tickers_data
from .server import app


@app.callback(
    Output('corr_table_window_x', 'data'),
    [Input('input_on_submit', 'value'),
     Input('submit_val_rel_p', 'n_clicks')],
    [State('input_on_submit_rel_p', 'value')]
)
def get_correlation_table_window_x(TICKER, n_clicks, MULTP_TICKERS):
    '''
    :return: Correlation table of the securities
    '''
    data = all_tickers_data.loc[:,MULTP_TICKERS]
    ticker_data = all_tickers_data.loc[:,TICKER]
    dataframe = pd.DataFrame()
    window_list = [15, 30, 90, 120]
    for window in window_list:
        for i in list(MULTP_TICKERS):
            dataframe[f'{TICKER}_{i}_{window}'] = ticker_data.rolling(window).corr(data[i])
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
    df['1y 30d corr high'] = rolling_30d_max
    df['1y 30d corr low'] = rolling_30d_min
    df.index = MULTP_TICKERS
    df = df.reset_index().rename(columns={'index':'vs'})
    return df.round(2).to_dict('records')

@app.callback(
    Output('performance_table', 'children'),
    [Input('input_on_submit', 'value'),
     Input('submit_val_rel_p', 'n_clicks')],
    [State('input_on_submit_rel_p', 'value')]
)
def get_performance(TICKER, n_clicks, MULTP_TICKERS):
    window_names = ['ticker','daily','weekly','monthly','quarterly','yearly', 'vs 52w max', 'vs 52w min']
    df = pd.DataFrame()
    ticker_list = [TICKER] + MULTP_TICKERS
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
        df[ticker] = results
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
    data = all_tickers_data.loc[:,MULTP_TICKERS]
    ticker_data = all_tickers_data.loc[:,TICKER]
    df = pd.DataFrame()
    range = [2, 6, 21, 63, 252]
    for i in list(MULTP_TICKERS):
        results = []
        latest_i = data[i].iloc[-1]
        latest_td = ticker_data[-1]
        for time in range:
            results.append(((latest_td - ticker_data[-time]) / latest_td) - ((latest_i - data[i].iloc[-time]) / latest_i))
        results = ["{:.2%}".format(y) for y in results]
        df[f'{i}'] = results
    df = df.T.reset_index()
    df.columns = window_names_rel_performance
    return dbc.Table.from_dataframe(df, bordered=True)















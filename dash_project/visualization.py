import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.tools as tls

from dash.dependencies import Input, Output, State
from dash_project.get_data import get_data, all_tickers_data
from dash_project.get_data import getClose_all_tickers
from .server import app

@app.callback(
    Output('correlation_chart', 'figure'),
    [Input('input_on_submit', 'value'),
     Input('submit_val_rel_p', 'n_clicks')],
    [State('input_on_submit_rel_p', 'value')]
)
def get_correlation_chart(TICKER, n_clicks, MULTP_TICKERS):
    data = all_tickers_data.loc[:,MULTP_TICKERS]
    ticker_data = all_tickers_data.loc[:,TICKER]
    dataframe = pd.DataFrame()
    window_list = [30]
    for window in window_list:
        for i in list(MULTP_TICKERS):
            dataframe[f'{TICKER}_{i}_{window}'] = ticker_data.rolling(window).corr(data[i])
    l = int(len(dataframe.columns)/len(window_list))

    fig = go.Figure()
    x = data.index
    for i in list(dataframe.columns):
        fig.add_trace((go.Scatter(x=x, y=dataframe[i], text=i, name=i[len(TICKER)+1:-3])))
    fig.update_xaxes(title='date')
    fig.update_yaxes(title='correlation')
    return fig

@app.callback(
    Output('graph_of_chart', 'figure'),
    Input('input_on_submit', 'value'))
def get_chart(input_value):
    '''
    :param data: Dataframe from get_data() function
    :return: Plots a graph and a moving average of the security' closing prices
    '''
    data = all_tickers_data[input_value]
    fig = go.Figure(go.Scatter(
        x=data.index,
        y=data,
        name='price'))
    fig.update_xaxes(title='date')
    fig.update_yaxes(title='price')
    return fig

# @app.callback(
#     Output('chart_title', 'children'),
#     Input('input_on_submit', 'value')
# )
# def chart_title(input_value):
#     return 'Chart of {}'.format(input_value)
#
# # @app.callback(
# #     Output('performance_table_title', 'children'),
# #     Input('input_on_submit', 'value')
# # )
# # def performance_table_title(input_value):
# #     return 'Performance of {}'.format(input_value)
#
# @app.callback(
#     Output('relative_performance_table_title', 'children'),
#     Input('input_on_submit', 'value')
# )
# def get_relative_performance_table_title(input_value):
#     return 'Relative performance of selected tickers vs {}'.format(input_value)
#
# @app.callback(
#     Output('correlation_table_title', 'children'),
#     Input('input_on_submit', 'value')
# )
# def get_relative_performance_table_title(input_value):
#     return 'Correlation table of selected tickers vs {}'.format(input_value)
#
# @app.callback(
#     Output('correlation_chart_title', 'children'),
#     Input('input_on_submit', 'value')
# )
# def get_relative_performance_table_title(input_value):
#     return '30D rolling correlation chart of selected tickers vs {}'.format(input_value)

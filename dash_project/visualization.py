import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.tools as tls

from dash.dependencies import Input, Output, State
from dash_project.get_data import get_data, all_tickers_data
from .server import app


@app.callback(
    Output('correlation_chart', 'figure'),
    [Input('input_on_submit', 'value'),
     Input('submit_val_rel_p', 'n_clicks')],
    [State('input_on_submit_rel_p', 'value')]
)
def get_correlation_chart(TICKER, n_clicks, MULTP_TICKERS):
    MULTP_TICKERS = [i + '_close' for i in MULTP_TICKERS]
    data = all_tickers_data.loc[:,MULTP_TICKERS]
    ticker_data = all_tickers_data.loc[:,f'{TICKER}_close']
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
    fig.update_layout(yaxis_range=[-1,1])
    return fig

@app.callback(
    Output('graph_of_chart', 'figure'),
    [Input('input_on_submit', 'value')]
)
def get_chart(TICKER):
    data = all_tickers_data.loc[:,f'{TICKER}_close']
    fig = go.Figure(go.Scatter(
        x=data.index,
        y=data,
        name='price'))
    fig.update_xaxes(title='date')
    fig.update_yaxes(title='price')
    return fig

# def create_z_score_plot(list_of_i_and_date, path_to_figure):
#     weeks = []
#     for i in range(0,156):
#         weeks.append(datetime.now() - relativedelta(weeks=i))
#     weeks.reverse()
#
#     z_score_list_one_year = get_list_of_z_scores(list_of_i_and_date, 1)
#     z_score_list_three_year = get_list_of_z_scores(list_of_i_and_date, 3)
#     z_score_list_one_year.reverse()
#     z_score_list_three_year.reverse()
#
#     fig = go.Figure(go.Scatter(
#         x=weeks,
#         y=z_score_list_one_year,
#         name='z-score 1y'
#     ))
#     fig.add_trace(go.Scatter(
#         x=weeks,
#         y=z_score_list_three_year,
#         name='z-score 3y'
#         )
#     )
#     fig.update_xaxes(title='date')
#     fig.update_yaxes(title='zscore')
#     return fig
import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from .server import app
from dash_project.get_data import ticker_list

from dash_project.performance import get_correlation_table_window_x
from dash_project.rescaled_range import hurst, hurst_range
from dash_project.visualization import get_chart
from dash.dependencies import Input, Output, State

# column names
window_names_p = ['ticker','daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'vs 52w max', 'vs 52w min']
window_names_rel_p = ['vs', 'daily', 'weekly', 'monthly', 'quarterly', 'yearly']
window_names_corr_table = ['vs','15D','30D','90D','120D','1y 30d corr high','1y 30d corr low']

app.config['suppress_callback_exceptions'] = True

controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label('Comp Tickers'),
                dcc.Dropdown(
                    id='input_on_submit_rel_p',
                    options=[{'label': x, 'value': x} for x in ticker_list],
                    multi=True,
                    placeholder='Select ticker(s)',
                    value=['XLY','XLF','XLV','XLK','XLP','XLI','XLB','XLE','XLU','XLRE','XLC']
                ),
                dbc.Button(
                    'Submit tickers',
                    id='submit_val_rel_p'
                )
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label('Base Ticker'),
                dbc.Input(
                    id='input_on_submit',
                    value='SPY',
                    placeholder='Input ticker'
                )

            ]
        )
    ]
)

sector_performance = html.Div(
    [
        html.H4('Sector performance'),
        html.Div(
            id='performance_table'
        ),
        html.H4('Relative sector performance'),
        html.Div(
            id='relative_p'
        )

    ]
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    controls,
                    width='auto'
                ),
                dbc.Col(
                    dcc.Graph(
                        id='graph_of_chart'),
                    width='auto'),
            ],
        ),
        dbc.Row(
            [
                dbc.Col(
                    sector_performance,
                width='auto')
            ]
        )
    ], fluid=True
)







# app.layout = html.Div(children=[
#     dcc.Tabs([
#         dcc.Tab(label='Performance', children=[
#             html.Div([
#                 dcc.Dropdown(
#                     id='input_on_submit_rel_p',
#                     options=[{'label': x, 'value': x} for x in ticker_list],
#                     multi=True,
#                     placeholder='Select ticker(s)',
#                     value=['XLY','XLF','XLV','XLK','XLP','XLI','XLB','XLE','XLU','XLRE','XLC']
#                 ),
#                 html.Button(
#                     'Submit tickers',
#                     id='submit_val_rel_p'
#                 )
#             ]),
#
#             html.Br(),
#             html.Div([
#                 dcc.Input(
#                     id='input_on_submit',
#                     value='SPY',
#                     placeholder='Input ticker'
#                 )
#             ]),
#
#             html.Br(),
#             html.Div([
#                 html.Div(
#                     id='chart_title'
#                 ),
#                 dcc.Graph(
#                     id='graph_of_chart'
#                 )
#             ]),
#
#             html.Br(),
#             html.Div([
#                 html.Div(
#                     'Sector performance'
#                 ),
#                 dash_table.DataTable(
#                     id='performance_table',
#                     columns=[{'name': c, 'id': c} for c in window_names_p]
#                 )
#             ]),
#
#             html.Br(),
#             html.Div([
#                 html.Div(
#                     id='relative_performance_table_title'
#                 ),
#                 dash_table.DataTable(
#                     id='relative_p',
#                     columns=[{'name': c, 'id': c} for c in window_names_rel_p]
#                 )
#             ])
#         ]),
#
#         dcc.Tab(label='Correlations', children=[
#             html.Div([
#                 html.Div(
#                     id='correlation_table_title'
#                 ),
#                 dash_table.DataTable(
#                     id='corr_table_window_x',
#                     columns=[{"name": x, "id": x} for x in window_names_corr_table]
#                 )
#             ]),
#
#             html.Br(),
#             html.Div([
#                 html.Div(
#                     id='correlation_chart_title'
#                 )
#                 ,
#                 dcc.Graph(
#                         id='correlation_chart'
#                 )
#             ])
#         ])
#         # ,
#
#         # dcc.Tab(label='Volatility', children=[
#         #     dcc.Graph(
#         #         id='R/S values',
#         #         figure=hurst(ticker_data)[0]
#         #     ),
#         #     dcc.Graph(
#         #         id='R/S cycle length',
#         #         figure=hurst_range(ticker_data)
#         #     )
#         # ])
#
#     ])
# ])







import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd

from .server import app
from dash_project.get_data import ticker_list, all_tickers_data
from dash_project.cftc_analyser import cftc_metrics_non_comm, get_asset_lists
from dash_project.performance import factor_sector_performance, get_performance, relative_performance, fx_performance
from dash_project.rescaled_range import hurst_regression_fig, hurst, hurst_cyle_graph, realised_vol, realised_vol_graph
from dash.dependencies import Input, Output, State


app.config.suppress_callback_exceptions = True

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Macro manager", className="display-4"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Performance", href="/performance", active="exact"),
                dbc.NavLink("Correlations", href="/correlations", active="exact"),
                dbc.NavLink("Volatility", href="/volatility", active="exact"),
                dbc.NavLink("CFTC data", href="/cftc", active="exact"),
                dbc.NavLink("Portfolio", href="/portfolio", active="exact")

            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

# style_dc = [{
#                'if': {
#                    'filter_query': '{1y zscore} < -1.5',
#                    'column_id': '1y zscore'},
#                'backgroundColor':'tomato',
#                'color':'white'},\
#            {
#                'if': {
#                    'filter_query': '{1y zscore} > 1.5',
#                    'column_id': '1y zscore'},
#                'backgroundColor': '#3D9970',
#                'color': 'white'},\
#            {
#                'if': {
#                    'filter_query': '{3y zscore} < -1.5',
#                    'column_id': '3y zscore'},
#                'backgroundColor': 'tomato',
#                'color': 'white'},\
#            {
#                'if': {
#                    'filter_query': '{3y zscore} > 1.5',
#                    'column_id': '3y zscore'},
#                'backgroundColor': '#3D9970',
#                'color': 'white'}]

@app.callback(
    Output('graph_of_chart', 'figure'),
    [Input('submit_val', 'n_clicks')],
    [State('input_on_submit', 'value')]
)
def get_chart(n_clicks, TICKER):
    data = all_tickers_data.loc[:,f'{TICKER}_close']
    fig = go.Figure(go.Scatter(
        x=data.index,
        y=data,
        name='price'))
    fig.update_xaxes(title='date')
    fig.update_yaxes(title='price')
    fig.update_layout(
        title={
            'text': f"{TICKER}",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    return fig

@app.callback(
    Output('correlation_chart', 'figure'),
    [Input('submit_val_corr', 'n_clicks'),
     Input('submit_val_corr_drop', 'n_clicks')],
    [State('input_on_submit_corr', 'value'),
     State('input_on_submit_corr_drop', 'value')])
def get_correlation_chart(n_clicks, n_clicks_corr, TICKER, MULTP_TICKERS):
    MULTP_TICKERS = [i + '_close' for i in MULTP_TICKERS]
    data = all_tickers_data.loc[:, MULTP_TICKERS]
    ticker_data = all_tickers_data.loc[:, f'{TICKER}_close']
    dataframe = pd.DataFrame()
    window_list = [30]
    for window in window_list:
        for i in list(MULTP_TICKERS):
            dataframe[f'{TICKER}_{i}_{window}'] = ticker_data.rolling(window).corr(data[i])
    l = int(len(dataframe.columns) / len(window_list))
    fig = go.Figure()
    x = data.index
    for i in list(dataframe.columns):
        fig.add_trace((go.Scatter(x=x, y=dataframe[i], name=i[len(TICKER)+1:-9])))
    fig.update_xaxes(title='date')
    fig.update_yaxes(title='correlation')
    fig.update_layout(
        yaxis_range=[-1, 1],
        title={
            'text': f"{TICKER} 30D correlations",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'}
    )
    return fig

@app.callback(
    Output('rs_regression_graph', 'figure'),
    [Input('vol_submit', 'n_clicks')],
    [State('vol_input', 'value')]
)
def vol_regression_graph(n_clicks, value):
    return hurst_regression_fig(hurst(value))

@app.callback(
    Output('rs_cycle_graph', 'figure'),
    [Input('vol_submit', 'n_clicks')],
    [State('vol_input', 'value')]
)
def vol_cycle_graph(n_clicks, value):
    return hurst_cyle_graph(value)

@app.callback(
    Output('realised_vol_graph', 'figure'),
    [Input('vol_submit', 'n_clicks')],
    [State('vol_input', 'value')]
)
def vol_graph(n_clicks, value):
    return realised_vol_graph(realised_vol(value))

@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    if pathname == "/":
        return html.P("This is the content of the home page!")
    elif pathname == "/performance":
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Br(),
                    html.H4('Base Ticker'),
                    dcc.Dropdown(
                        id='input_on_submit',
                        options=[{'label': x, 'value': x} for x in ticker_list],
                        value='SPX',
                        placeholder='Select security',
                        multi=False
                    ),
                    html.Br(),
                    dbc.Button(
                        'Submit ticker',
                        id='submit_val'
                    ),
                    html.Br(),
                    html.Br(),
                    html.H4('Comp Tickers'),
                    dcc.Dropdown(
                        id='input_on_submit_rel_p',
                        options=[{'label': x, 'value': x} for x in ticker_list],
                        multi=True,
                        placeholder='Select ticker(s)',
                        value=['XLY', 'XLF','XLV','XLK','XLP','XLI','XLB','XLE','XLU']
                    ),
                    html.Br(),
                    dbc.Button(
                        'Submit ticker(s)',
                        id='submit_val_rel_p'
                    )
                ]),
            ]),
            dbc.Row(
                dbc.Col([
                    dcc.Graph(
                        id='graph_of_chart')
                ])
            ),
            dbc.Row([
                dbc.Col([
                    html.Br(),
                    html.H4('Sector performance'),
                    html.Div(
                        id='performance_table'
                    )
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    html.Br(),
                    html.H4('Relative sector performance'),
                    html.Div(
                        id='relative_p'
                    )
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    html.Br(),
                    html.H4('Factor Sector Performance'),
                    html.Div(
                        factor_sector_performance()
                    )
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    html.Br(),
                    html.H4('FX Performance'),
                    html.Div(
                        fx_performance()
                    )
                ])
            ])
        ])

    elif pathname == "/correlations":
        return dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.Br(),
                        html.H4('Base Ticker'),
                        dbc.Input(
                            id='input_on_submit_corr',
                            value='UUP',
                            placeholder='Input ticker'
                        ),
                        html.Br(),
                        dbc.Button(
                            'Submit ticker',
                            id='submit_val_corr'
                        ),
                        html.Br(),
                        html.Br(),
                        html.H4('Comp Tickers'),
                        dcc.Dropdown(
                            id='input_on_submit_corr_drop',
                            options=[{'label': x, 'value': x} for x in ticker_list],
                            multi=True,
                            placeholder='Select ticker(s)',
                            value=['SPX','USO','DBC','GLD', 'BRR']
                        ),
                        html.Br(),
                        dbc.Button(
                            'Submit ticker(s)',
                            id='submit_val_corr_drop'
                        )

                    ])
                ]),
                dbc.Row([
                    dbc.Col(
                        dcc.Graph(
                            id='correlation_chart'
                        )
                    )
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H4('Correlation table'),
                            html.Div(
                                id='corr_table_window_x'
                            )
                        ])
                    ])
                ])
            ])

    elif pathname == '/volatility':
        return dbc.Container([
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.H4('Base Ticker'),
                        dcc.Dropdown(
                            id='vol_input',
                            options=[{'label': x, 'value': x} for x in ticker_list],
                            value='SPY',
                            placeholder='Select security',
                            multi=False
                        ),
                        html.Br(),
                        dbc.Button(
                            'Get chart',
                            id='vol_submit'
                        )
                    ])
                )
            ]),
            dbc.Row([
                dbc.Col([
                    html.Br(),
                    html.Div([
                        html.H4('R/S regression'),
                        html.Div([
                            dcc.Graph(id='rs_regression_graph')
                        ])
                    ])
                ]),
                dbc.Col([
                    html.Div([
                        html.H4('R/S cycle graph'),
                        html.Div([
                            dcc.Graph(id='rs_cycle_graph')
                        ])
                    ])
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4('Volatility'),
                        html.Div([
                            dcc.Graph(id='realised_vol_graph')
                        ])
                    ])
                ])
            ])
        ])

    elif pathname == '/cftc':
        return dbc.Container([
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.H4('Base Ticker'),
                        dcc.Dropdown(
                            id='cftc_input',
                            options=[{'label':x, 'value':x} for x in cftc_metrics_non_comm],
                            value='SPX',
                            placeholder='Select security',
                            multi=False
                        ),
                        html.Br(),
                        dbc.Button(
                            'Get chart',
                            id='cftc_submit'
                        ),
                    ])
                ),
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H4('CFTC positioning'),
                    html.Div(
                        id='cftc_positioning'
                    )
                ])
            ]),
            html.Br(),
            dbc.Row([
                dcc.Graph(
                    id='cftc_graph'
                )
            ]),
            dbc.Row(
                dbc.Col([
                    html.Div([
                        html.Br(),
                        html.Br(),
                        html.H4('Asset class selector'),
                        dcc.Dropdown(
                            id='cftc_input_df',
                            options=[{'label': x, 'value': x} for x in get_asset_lists()],
                            value=['SPX', '10Y UST', 'Crude Oil', 'Copper', 'Gold', 'USD', 'JPY', 'EUR', 'GBP', 'BTC'],
                            placeholder='Select security',
                            multi=True
                        ),
                        html.Br(),
                        dbc.Button(
                            'Get CFTC datatable',
                            id='cftc_submit_df'
                        )
                    ])
                ])
            ),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H4('CFTC Non-Commercial Datatable'),
                    html.Div(
                        id='cftc_datatable_non_comm'
                    )
                ]),
                dbc.Col([
                    html.H4('CFTC Commercial Datatable'),
                    html.Div(
                        id='cftc_datatable_comm'
                    )
                ])
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([

            ])
        ])

    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

content = html.Div(
    id="page-content",
    style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
])
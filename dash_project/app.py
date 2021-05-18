import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table

from .server import app
from dash_project.get_data import ticker_list
from dash_project.cftc_analyser import cftc_df
from dash_project.performance import factor_sector_performance
from dash.dependencies import Input, Output, State


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

sec_selector = html.Div(
    [
        html.Br(),
        html.H4('Base Ticker'),
        dbc.Input(
            id='input_on_submit',
            value='SPY',
            placeholder='Input ticker'
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
            value=['XLY', 'XLF', 'XLV', 'XLK', 'XLP', 'XLI', 'XLB', 'XLE', 'XLU', 'XLRE', 'XLC']
        ),
        html.Br(),
        dbc.Button(
            'Submit ticker(s)',
            id='submit_val_rel_p'
        )
    ]
)

base_sec_selector = html.Div(
    [
        html.Br(),
        html.H4('Base Ticker'),
        dbc.Input(
            id='input_on_submit_base',
            value='SPY',
            placeholder='Input ticker'
        ),
        html.Br(),
        dbc.Button(
            'Submit ticker',
            id='submit_ticker_base'
        )
    ]
)

style_dc = [{
               'if': {
                   'filter_query': '{1y zscore} < -1.5',
                   'column_id': '1y zscore'},
               'backgroundColor':'tomato',
               'color':'white'},\
           {
               'if': {
                   'filter_query': '{1y zscore} > 1.5',
                   'column_id': '1y zscore'},
               'backgroundColor': '#3D9970',
               'color': 'white'},\
           {
               'if': {
                   'filter_query': '{3y zscore} < -1.5',
                   'column_id': '3y zscore'},
               'backgroundColor': 'tomato',
               'color': 'white'},\
           {
               'if': {
                   'filter_query': '{3y zscore} > 1.5',
                   'column_id': '3y zscore'},
               'backgroundColor': '#3D9970',
               'color': 'white'}]

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
                    sec_selector
                ]),
                dbc.Col(
                    dcc.Graph(
                        id='graph_of_chart')
                )
            ]),
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
            ])
        ])

    elif pathname == "/correlations":
        return dbc.Container([
                dbc.Row([
                    dbc.Col([
                        sec_selector
                    ]),
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
                    base_sec_selector
                )
            ]),
            dbc.Row([
                dbc.Col([
                    html.Br(),
                    html.Br(),
                    html.H4('R/S regression'),
                    dcc.Graph(
                        id='rs_regression_graph'
                    )
                ]),
                dbc.Col([
                    html.Br(),
                    html.Br(),
                    html.H4('R/S cycle length'),
                    dcc.Graph(
                        id='rs_cycle'
                    )
                ])
            ])
        ])

    elif pathname == '/cftc':
        return dbc.Container([
            dbc.Row([
                dbc.Col(
                   base_sec_selector
                ),
                dbc.Col(

                )
            ]),
            dbc.Row([
                dbc.Col([
                    html.Br(),
                    html.Br(),
                    html.H4('CFTC Non-Commercial Net Long Positioning'),
                    dash_table.DataTable(
                        data=cftc_df.to_dict('records'),
                        columns=[{"name": i, "id": i} for i in cftc_df.columns],
                        sort_action='native',
                        editable=True,
                        style_data_conditional=style_dc
                    )
                ])
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
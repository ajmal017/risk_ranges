import dash
import dash_bootstrap_components as dbc

from flask import Flask


server = Flask('__name__')
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.UNITED])

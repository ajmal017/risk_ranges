import dash
import dash_bootstrap_components as dbc

from quart import Quart
from flask import Flask


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask('__name__')
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

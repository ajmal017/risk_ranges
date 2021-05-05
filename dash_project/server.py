from flask import Flask
import dash
from quart import Quart

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask('__name__')
app = dash.Dash(server=server, external_stylesheets=external_stylesheets)

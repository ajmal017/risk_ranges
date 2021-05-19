import pandas as pd
import plotly.graph_objects as go

from dash.dependencies import Input, Output, State
from dash_project.get_data import getData, all_tickers_data
from .server import app




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
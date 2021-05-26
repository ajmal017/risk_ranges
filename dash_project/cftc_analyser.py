import datetime
import urllib.request, shutil
import math
import yaml
import os
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from datetime import datetime
from dateutil.relativedelta import relativedelta
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots
from .server import app
from zipfile import ZipFile


num_of_entries = 0

three_years_ago = datetime.now() - relativedelta(years=3)
one_year_ago = datetime.now() - relativedelta(years=1)
three_months_ago = datetime.now() - relativedelta(months=3)
six_months_ago = datetime.now() - relativedelta(months=6)

extract_zip_files = True

def sortOnTime(val):
    return val[1]

def get_list_of_i_and_date_for_metric(expected_row_names, num_of_entries, date_list, name_list):
    the_list = []
    for expected_row_name in expected_row_names:
        for i in range(0, num_of_entries):
            row_name = name_list[i]
            if row_name == expected_row_name:
                the_list.append((i, date_list[i]))
    the_list.sort(key=sortOnTime)
    return the_list

def get_latest_i(list_of_i_and_date, end_date=datetime.now()):
    latest_i = list_of_i_and_date[-1][0]
    for i, date in reversed(list_of_i_and_date):
        if date < end_date:
            latest_i = i
            break
    return latest_i

def get_second_latest_i(list_of_i_and_date, latest_i):
    previous_i = 0
    second_latest_i = 0
    for i, date in list_of_i_and_date:
        if i == latest_i:
            second_latest_i = previous_i
        else:
            previous_i = i
    return second_latest_i

def get_x_year_min_max(list_of_i_and_date, begin_date, values):
    minimum = float('inf')
    maximum = float('-inf')
    for i, date in list_of_i_and_date:
        if date > begin_date:
            current = values[i]
            if current < minimum:
                minimum = current
            if current > maximum:
                maximum = current
    return minimum, maximum

def calculate_x_year_avg(list_of_i_and_date, begin_date, values, end_date=datetime.now()):
    x_year_avg = 0
    entry_count = 0
    for i, date in list_of_i_and_date:
        if date >= begin_date and date <= end_date:
            x_year_avg += values[i]
            entry_count += 1
    if entry_count != 0:
        x_year_avg /= entry_count
    return x_year_avg

def calculate_z_score(list_of_i_and_date, begin_date, values, end_date=datetime.now()):
    z_score = 0
    entry_count = 0
    latest_i = get_latest_i(list_of_i_and_date, end_date)
    latest = values[latest_i]

    x_year_avg = calculate_x_year_avg(list_of_i_and_date, begin_date, values, end_date)
    for i, date in list_of_i_and_date:
        if date >= begin_date and date <= end_date:
            z_score += pow((values[i] - x_year_avg), 2)
            entry_count += 1

    if entry_count != 0:
        z_score /= entry_count
        z_score = math.sqrt(z_score)
        if z_score != 0:
            z_score = (latest - x_year_avg) / z_score
    return z_score

def get_list_of_z_scores(list_of_i_and_date, year_count, values):
    the_list = []
    for i in range(0, 156):
        begin_date = datetime.now() - relativedelta(years=year_count, weeks=i)
        end_date = datetime.now() - relativedelta(weeks=i)
        the_list.append(calculate_z_score(list_of_i_and_date, begin_date, values, end_date))
    return the_list

def get_list_of_net_positioning(list_of_i_and_date, begin_date, values):
    the_list = []
    for i, date in list_of_i_and_date:
        if date > begin_date:
            current = values[i]
            the_list.append(current)
    return the_list

def get_cot_zip_file(url, file_name):
    with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

def getLists():
    NAME = "Market_and_Exchange_Names"
    DATE = "Report_Date_as_MM_DD_YYYY"
    INTEREST = "Open_Interest_All"
    NON_COMM_LONG = "NonComm_Positions_Long_All"
    NON_COMM_SHORT = "NonComm_Positions_Short_All"
    COMM_LONG = "Comm_Positions_Long_All"
    COMM_SHORT = "Comm_Positions_Short_All"

    name_list = []
    date_list = []
    interest_list = []
    non_comm_long_list = []
    non_comm_short_list = []
    comm_long_list = []
    comm_short_list = []

    DATA_DIR = "dash_project/cftc_data"
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    years = [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
    for year in years:
        file = f'{DATA_DIR}/{year}.zip'
        get_cot_zip_file(f'https://www.cftc.gov/files/dea/history/dea_com_xls_{year}.zip', file)

    data_files = os.listdir(DATA_DIR)
    for data_file in data_files:
        if '.zip' in data_file:
            data_file_name = data_file[:-4]
            if extract_zip_files:
                with ZipFile(f"{DATA_DIR}/{data_file}", 'r') as f:
                    listOfFileNames = f.namelist()
                    fileName = listOfFileNames[0]
                    f.extractall("dash_project/tmp")
                    os.replace(f"dash_project/tmp/{fileName}", f"dash_project/tmp/{data_file_name}.xls")

            xl = pd.ExcelFile(f"/tmp/{data_file_name}.xls")
            df = pd.read_excel(xl, usecols=[NAME, DATE, INTEREST, NON_COMM_LONG, NON_COMM_SHORT, COMM_LONG, COMM_SHORT])
            name_list += list(df[NAME])
            date_list += list(df[DATE])
            interest_list += list(df[INTEREST])
            non_comm_long_list += list(df[NON_COMM_LONG])
            non_comm_short_list += list(df[NON_COMM_SHORT])
            comm_long_list += list(df[COMM_LONG])
            comm_short_list += list(df[COMM_SHORT])
    return name_list, date_list, interest_list, non_comm_long_list, non_comm_short_list, comm_long_list, comm_short_list

def get_values(list_of_i_and_date, list_long, list_short=None):
    latest_i = get_latest_i(list_of_i_and_date)
    second_latest_i = get_second_latest_i(list_of_i_and_date, latest_i)
    if list_short is not None:
        diff = [(a-b) for a,b in zip(list_long,list_short)]
    else:
        diff = list_long
    latest = diff[latest_i]
    second_latest = diff[second_latest_i]
    ww_change = latest - second_latest
    minimum, maximum = get_x_year_min_max(list_of_i_and_date, three_years_ago, diff)
    three_month_avg = calculate_x_year_avg(list_of_i_and_date, three_months_ago, diff)
    six_month_avg = calculate_x_year_avg(list_of_i_and_date, six_months_ago, diff)
    one_year_avg = calculate_x_year_avg(list_of_i_and_date, one_year_ago, diff)
    three_year_avg = calculate_x_year_avg(list_of_i_and_date, three_years_ago, diff)
    z_score_one_year = calculate_z_score(list_of_i_and_date, one_year_ago, diff)
    z_score_three_years = calculate_z_score(list_of_i_and_date, three_years_ago, diff)
    return latest_i, second_latest_i, latest, second_latest, ww_change, minimum, maximum, three_month_avg, six_month_avg, one_year_avg, three_year_avg, z_score_one_year, z_score_three_years

def get_CFTC_Dataframe(name_list, date_list, long_list, short_list):
    num_of_entries = len(name_list)
    cwd = os.getcwd()
    with open("dash_project/metrics.yaml", 'r') as yf:
        metrics = yaml.safe_load(yf)
    cftc_df = pd.DataFrame()
    for asset_class in metrics:
        for metric in metrics[asset_class]:
            list_of_i_and_date = get_list_of_i_and_date_for_metric(metrics[asset_class][metric], num_of_entries, date_list, name_list)
            latest_i, second_latest_i, latest, second_latest, ww_change, minimum, maximum, three_month_avg, six_month_avg, one_year_avg, three_year_avg, z_score_one_year, z_score_three_years = get_values(list_of_i_and_date, long_list, short_list)

            cftc_df[metric] = [metric, latest, ww_change, three_month_avg, six_month_avg, one_year_avg, three_year_avg,
                               maximum, minimum, z_score_one_year, z_score_three_years]
    cftc_df = cftc_df.T
    cftc_df.columns = ['metric', 'latest', 'w/w change', '3m ave', '6m ave', '1y ave','3y ave', '3y max', '3y min', '1y zscore', '3y zscore']
    for column in cftc_df.iloc[:, 1:]:
        cftc_df[column] = cftc_df[column].astype(float)
    return cftc_df.round(2), cftc_df.index, num_of_entries


name_list, date_list, interest_list, non_comm_long_list, non_comm_short_list, comm_long_list, comm_short_list  = getLists()
cftc_df_non_comm, cftc_metrics_non_comm, n_entries_non_comm = get_CFTC_Dataframe(name_list, date_list, non_comm_long_list, non_comm_short_list)
cftc_df_comm, cftc_metrics_comm, n_entries_comm = get_CFTC_Dataframe(name_list, date_list, comm_long_list, comm_short_list)


@app.callback(
    Output('cftc_datatable_non_comm', 'children'),
    [Input('cftc_submit_df', 'n_clicks')],
    [State('cftc_input_df', 'value')]
)
def get_CFTC_df_selection(n_clicks, MULTP_ASSETS):
    return dbc.Table.from_dataframe(
        cftc_df_non_comm.loc[MULTP_ASSETS, :],
        bordered=True)

@app.callback(
    Output('cftc_datatable_comm', 'children'),
    [Input('cftc_submit_df', 'n_clicks')],
    [State('cftc_input_df', 'value')]
)
def get_CFTC_df_selection(n_clicks, MULTP_ASSETS):
    return dbc.Table.from_dataframe(
        cftc_df_comm.loc[MULTP_ASSETS, :],
        bordered=True)

@app.callback(
    Output('cftc_graph', 'figure'),
    [Input('cftc_submit', 'n_clicks')],
    [State('cftc_input', 'value')]
)
def create_z_score_plot(n_clicks, TICKER):
    num_of_entries = len(name_list)
    weeks = []
    for i in range(0,156):
        weeks.append(datetime.now() - relativedelta(weeks=i))
    weeks.reverse()
    cwd = os.getcwd()
    with open("dash_project/metrics.yaml", 'r') as yf:
        metrics = yaml.safe_load(yf)

    for asset_class in metrics:
        for metric in metrics[asset_class]:
            if metric == TICKER:
                list_of_i_and_date = get_list_of_i_and_date_for_metric(metrics[asset_class][metric], num_of_entries, date_list, name_list)

    diff_non_comm = [(a - b) for a, b in zip(non_comm_long_list, non_comm_short_list)]
    z_score_list_one_year_non_comm = get_list_of_z_scores(list_of_i_and_date, 1, diff_non_comm)
    z_score_list_three_year_non_comm = get_list_of_z_scores(list_of_i_and_date, 3, diff_non_comm)
    z_score_list_one_year_non_comm.reverse()
    z_score_list_three_year_non_comm.reverse()

    diff_comm = [(a - b) for a, b in zip(comm_long_list, comm_short_list)]
    z_score_list_one_year_comm = get_list_of_z_scores(list_of_i_and_date, 1, diff_comm)
    z_score_list_three_year_comm = get_list_of_z_scores(list_of_i_and_date, 3, diff_comm)
    z_score_list_one_year_comm.reverse()
    z_score_list_three_year_comm.reverse()

    z_score_list_one_year_open_interest = get_list_of_z_scores(list_of_i_and_date, 1, interest_list)
    z_score_list_three_year_open_interest = get_list_of_z_scores(list_of_i_and_date, 3, interest_list)
    z_score_list_one_year_open_interest.reverse()
    z_score_list_three_year_open_interest.reverse()

    non_comm_net_positioning_list = get_list_of_net_positioning(list_of_i_and_date, three_years_ago, diff_non_comm)
    comm_net_positioning_list = get_list_of_net_positioning(list_of_i_and_date, three_years_ago, diff_comm)
    net_open_interest_list = get_list_of_net_positioning(list_of_i_and_date, three_years_ago, interest_list)

    fig = make_subplots(rows=3, cols=2,
                        subplot_titles=("Z-scores non_comm",
                                        "Z-scores comm",
                                        "Net positioning non_comm",
                                        "Net positioning Comm",
                                        "Z-scores open interest,",
                                        "Open interest"))

    fig.add_trace(go.Scatter(x=weeks, y=z_score_list_one_year_non_comm, name='1y (non_comm)'),
                  row=1, col=1,
                  ),
    fig.add_trace(go.Scatter(x=weeks, y=z_score_list_three_year_non_comm, name='3y (non_comm)'),
                  row=1, col=1
                  )

    fig.add_trace(go.Scatter(x=weeks, y=z_score_list_one_year_comm, name='1y (comm)'),
                  row=1, col=2,
                  ),
    fig.add_trace(go.Scatter(x=weeks, y=z_score_list_three_year_comm, name='3y (comm)'),
                  row=1, col=2
                  )

    fig.add_trace(go.Bar(x=weeks, y=non_comm_net_positioning_list, name="Net Pos (non_comm)"),
                  row=2, col=1
                  )
    fig.add_trace(go.Bar(x=weeks, y=comm_net_positioning_list, name="Net Pos (comm)"),
                  row=2, col=2
                  )

    fig.add_trace(go.Scatter(x=weeks, y=z_score_list_one_year_open_interest, name='1y (OI)'),
                  row=3, col=1,
                  ),
    fig.add_trace(go.Scatter(x=weeks, y=z_score_list_three_year_open_interest, name='3y (OI)'),
                  row=3, col=1,
                  ),
    fig.add_trace(go.Bar(x=weeks, y=net_open_interest_list, name="OI"),
                  row=3, col=2
                  )

    fig.update_xaxes(title_text="date")
    fig.update_yaxes(title_text="z_score", row=1, col=1)
    fig.update_yaxes(title_text="z_score", row=1, col=2)
    fig.update_yaxes(title_text="net contracts", row=2, col=1)
    fig.update_yaxes(title_text="net_contracts", row=2, col=2)
    fig.update_yaxes(title_text="z_score", row=3, col=1)
    fig.update_yaxes(title_text="net_contracts", row=3, col=2)

    fig.update_layout(
        width=1200,
        height=1250)
    return fig

def get_asset_lists():
    with open("dash_project/metrics.yaml", 'r') as yf:
        metrics = yaml.safe_load(yf)
    options = []
    for asset_class in metrics:
        for metric in metrics[asset_class]:
            options.append(metric)
    return options

@app.callback(
    Output('cftc_positioning', 'children'),
    [Input('cftc_submit', 'n_clicks')],
    [State('cftc_input', 'value')]
)
def get_cftc_positioning(n_clicks, TICKER):
    num_of_entries = len(name_list)
    weeks = []
    for i in range(0, 156):
        weeks.append(datetime.now() - relativedelta(weeks=i))
    weeks.reverse()
    cwd = os.getcwd()
    with open("dash_project/metrics.yaml", 'r') as yf:
        metrics = yaml.safe_load(yf)

    df = pd.DataFrame()
    done = False
    for asset_class in metrics:
        for metric in metrics[asset_class]:
            if metric == TICKER:
                list_of_i_and_date = get_list_of_i_and_date_for_metric(metrics[asset_class][metric], num_of_entries, date_list, name_list)

                investor = 'Open interest'
                latest_i, second_latest_i, latest, second_latest, ww_change, minimum, maximum, three_month_avg, six_month_avg, one_year_avg, three_year_avg, z_score_one_year, z_score_three_years = get_values(list_of_i_and_date, interest_list)
                df[investor] = [investor, latest, ww_change, three_month_avg, six_month_avg, one_year_avg, three_year_avg, maximum, minimum, z_score_one_year, z_score_three_years]

                investor = 'Non_commercial'
                latest_i, second_latest_i, latest, second_latest, ww_change, minimum, maximum, three_month_avg, six_month_avg, one_year_avg, three_year_avg, z_score_one_year, z_score_three_years = get_values(list_of_i_and_date, non_comm_long_list, non_comm_short_list)
                df[investor] = [investor, latest, ww_change, three_month_avg, six_month_avg, one_year_avg, three_year_avg, maximum, minimum, z_score_one_year, z_score_three_years]

                investor = 'Commercial'
                latest_i, second_latest_i, latest, second_latest, ww_change, minimum, maximum, three_month_avg, six_month_avg, one_year_avg, three_year_avg, z_score_one_year, z_score_three_years = get_values(list_of_i_and_date, comm_long_list, comm_short_list)
                df[investor] = [investor, latest, ww_change, three_month_avg, six_month_avg, one_year_avg, three_year_avg, maximum, minimum, z_score_one_year, z_score_three_years]
                done = True
                break
        if done:
            break

    df = df.T
    df.columns = ['class', 'latest', 'w/w change', '3m ave', '6m ave', '1y ave', '3y ave', '3y max', '3y min', '1y zscore', '3y zscore']
    for column in df.iloc[:, 1:]:
        df[column] = df[column].astype(float)
    return dbc.Table.from_dataframe(
        df.round(2), bordered=True)



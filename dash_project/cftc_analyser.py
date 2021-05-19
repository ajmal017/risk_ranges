import datetime
import zipfile, urllib.request, shutil
import math
import yaml
import os
import pandas as pd
import time

from datetime import datetime
from dateutil.relativedelta import relativedelta
from zipfile import ZipFile



START_TIME = time.time()
print("------- %s seconds ------------" % (time.time() - START_TIME))

DATA_DIR = "dash_project/cftc_data"

NAME = "Market_and_Exchange_Names"
DATE = "Report_Date_as_MM_DD_YYYY"
INTEREST = "Open_Interest_All"
LONG = "NonComm_Positions_Long_All"
SHORT = "NonComm_Positions_Short_All"

name_list = []
date_list = []
interest_list = []
long_list = []
short_list = []

num_of_entries = 0

three_years_ago = datetime.now() - relativedelta(years=3)
one_year_ago = datetime.now() - relativedelta(years=1)
three_months_ago = datetime.now() - relativedelta(months=3)
six_months_ago = datetime.now() - relativedelta(months=6)

extract_zip_files = True

def sortOnTime(val):
    return val[1]

def get_list_of_i_and_date_for_metric(expected_row_names):
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

def get_x_year_min_max(list_of_i_and_date, begin_date, end_date=datetime.now()):
    minimum = float('inf')
    maximum = float('-inf')
    for i, date in list_of_i_and_date:
        if date > begin_date:
            current = long_list[i] - short_list[i]
            if current < minimum:
                minimum = current
            if current > maximum:
                maximum = current
    return minimum, maximum

def calculate_x_year_avg(list_of_i_and_date, begin_date, end_date=datetime.now()):
    x_year_avg = 0
    entry_count = 0
    for i, date in list_of_i_and_date:
        if date >= begin_date and date <= end_date:
            x_year_avg += (long_list[i] - short_list[i])
            entry_count += 1
    if entry_count != 0:
        x_year_avg /= entry_count
    return x_year_avg

def calculate_z_score(list_of_i_and_date, begin_date, end_date=datetime.now()):
    z_score = 0
    entry_count = 0
    latest_i = get_latest_i(list_of_i_and_date, end_date)
    latest = long_list[latest_i] - short_list[latest_i]
    x_year_avg = calculate_x_year_avg(list_of_i_and_date, begin_date, end_date)
    for i, date in list_of_i_and_date:
        if date >= begin_date and date <= end_date:
            z_score += pow(((long_list[i] - short_list[i]) - x_year_avg), 2)
            entry_count += 1
    if entry_count != 0:
        z_score /= entry_count
        z_score = math.sqrt(z_score)
        if z_score != 0:
            z_score = (latest - x_year_avg) / z_score
    return z_score

def get_list_of_z_scores(list_of_i_and_date, year_count):
    the_list = []
    for i in range(0, 156):
        begin_date = datetime.now() - relativedelta(years=year_count, weeks=i)
        end_date = datetime.now() - relativedelta(weeks=i)
        the_list.append(calculate_z_score(list_of_i_and_date, begin_date, end_date))
    return the_list

def get_cot_zip_file(url, file_name):
    with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

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
        df = pd.read_excel(xl, usecols=[NAME, DATE, INTEREST, LONG, SHORT])
        name_list += list(df[NAME])
        date_list += list(df[DATE])
        interest_list += list(df[INTEREST])
        long_list += list(df[LONG])
        short_list += list(df[SHORT])

num_of_entries = len(name_list)
cwd = os.getcwd()
with open("dash_project/metrics.yaml", 'r') as yf:
    metrics = yaml.safe_load(yf)

cftc_df = pd.DataFrame()
for asset_class in metrics:
    for metric in metrics[asset_class]:
        list_of_i_and_date = get_list_of_i_and_date_for_metric(metrics[asset_class][metric])
        latest_i = get_latest_i(list_of_i_and_date)
        second_latest_i = get_second_latest_i(list_of_i_and_date, latest_i)
        latest = (long_list[latest_i] - short_list[latest_i])
        second_latest = (long_list[second_latest_i] - short_list[second_latest_i])
        ww_change = latest - second_latest
        minimum, maximum = get_x_year_min_max(list_of_i_and_date, three_years_ago)
        three_month_avg = calculate_x_year_avg(list_of_i_and_date, three_months_ago)
        six_month_avg = calculate_x_year_avg(list_of_i_and_date, six_months_ago)
        one_year_avg = calculate_x_year_avg(list_of_i_and_date, one_year_ago)
        three_year_avg = calculate_x_year_avg(list_of_i_and_date, three_years_ago)
        z_score_one_year = calculate_z_score(list_of_i_and_date, one_year_ago)
        z_score_three_years = calculate_z_score(list_of_i_and_date, three_years_ago)

        # create_z_score_plot(list_of_i_and_date, path_to_figure)

        cftc_df[metric] = [metric, latest, ww_change, three_month_avg, six_month_avg, one_year_avg,
                           maximum, minimum, z_score_one_year, z_score_three_years]

cftc_df = cftc_df.T
cftc_df.columns = ['metric','latest','w/w change','3m ave','6m ave','1y ave','3y max','3y min','1y zscore','3y zscore']

for column in cftc_df.iloc[:,1:]:
    cftc_df[column] = cftc_df[column].astype(float)

cftc_df = cftc_df.round(2)

print("------- %s seconds ------------" % (time.time() - START_TIME))



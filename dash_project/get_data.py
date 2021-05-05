import pandas as pd
import random
import numpy as np
import os
import glob

from dash.dependencies import Output, Input
from ib_insync import *
from .server import app


# https://groups.io/g/insync/topic/connecting_with_client_id/76168807?20,0,0,0::recentpostdate%2Fsticky,,,20,2,0,76168807

random_id = random.randint(0, 9999)
ib = IB()
ib.connect(host='127.0.0.1', port=7496, clientId=random_id)

def getTickerlist():
    data_files = os.listdir('dash_project/data/')
    sec_list = []
    for filename in data_files:
        df = pd.read_csv(f'dash_project/data/{filename}').iloc[:, 0]
        sec_list.append(df)
    flatList = []
    for elem in sec_list:
        flatList.extend(elem)
    return flatList

def getClose_all_tickers(securities_list):
    date_time = get_data(securities_list[0])[1]
    dataframe = pd.DataFrame()
    for i in securities_list:
        dataframe[i] = get_data(i)[2]
    dataframe = dataframe.set_index(date_time)

    for column in list(dataframe.columns):
        if 252 > len(dataframe[column].dropna()):
            dataframe = dataframe.drop(columns=[f'{column}'])
            data = get_data(column)[0].set_index('date').rename(columns={'close': f'{column}'})
            dataframe = dataframe.join(data, on='date')
    return dataframe.interpolate()

def data(TICKER, securities_list):
    date_time = get_data(securities_list[0])[1]
    dataframe = pd.DataFrame()
    for i in securities_list:
        dataframe[i] = get_data(i)[2]
    dataframe = dataframe.set_index(date_time)

    for column in list(dataframe.columns):
        if 252 > len(dataframe[column].dropna()):
            dataframe = dataframe.drop(columns=[f'{column}'])
            data = get_data(column)[0].set_index('date').rename(columns={'close': f'{column}'})
            dataframe = dataframe.join(data, on='date')
    dataframe = dataframe.interpolate()
    data = dataframe.iloc[:,:-1]
    ticker_data = dataframe.iloc[:,-1]
    return data, ticker_data, date_time, dataframe

def getSector_performance(securities_list):
    dataframe = pd.DataFrame()
    for i in securities_list:
        dataframe[i] = get_data(i)[2]
    df = pd.DataFrame()
    for column in list(dataframe.columns):
        data = np.array(dataframe[column])
        range = [2, 21, 63, 252]
        latest = data[-1]
        results = []
        for time in range:
            results.append((latest - data[-time]) / latest)
        results = ["{:.2%}".format(y) for y in results]
        df[column] = results
    window_names = ['1-Day%', 'MTD%', 'QTD%', 'YTD%']
    df['SECTOR'] = window_names
    df = df.set_index('SECTOR')
    return df.T

def get_data(Ticker):
    '''
    :param Ticker: Security Symbol/Ticker
    :return: Dataframe with Closing prices and Date of security

    TO DO; FIX CONTRACT FOR FUTURES
    '''

    path = "dash_project/data"
    all_files = glob.glob(os.path.join(path, "*.csv"))
    all_df = []
    for f in all_files:
        df = pd.read_csv(f, sep=',')
        all_df.append(df)
    ticker_list = pd.concat(all_df).set_index('Ticker')

    if not Ticker in list(ticker_list.index):
        print('Ticker not in list')

    elif ticker_list.loc[Ticker][0] == 'STK':
        contract = Stock(symbol=Ticker,
                         exchange=ticker_list.loc[Ticker][1],
                         currency=ticker_list.loc[Ticker][4])
        ib.qualifyContracts(contract)
        historical_data = ib.reqHistoricalData(
            contract,
            '',
            barSizeSetting='1 day',
            durationStr='1 Y',
            whatToShow='MIDPOINT',
            useRTH=True
        )

    elif ticker_list.loc[Ticker][0] == 'CASH':
        contract = Forex(pair=Ticker,
                         exchange=ticker_list.loc[Ticker][1],
                         symbol=ticker_list.loc[Ticker][4],
                         currency=ticker_list.loc[Ticker][6])
        ib.qualifyContracts(contract)
        historical_data = ib.reqHistoricalData(
            contract,
            '',
            barSizeSetting='1 day',
            durationStr='1 Y',
            whatToShow='MIDPOINT',
            useRTH=True
        )

    elif ticker_list.loc[Ticker][0] == 'FUT':
        contract = ContFuture(symbol=Ticker,
                              exchange=ticker_list.loc[Ticker][1],
                              localSymbol=ticker_list.loc[Ticker][5],
                              multiplier=ticker_list.loc[Ticker][3],
                              currency=ticker_list.loc[Ticker][4])
        ib.qualifyContracts(contract)
        historical_data = ib.reqHistoricalData(
            contract,
            '',
            barSizeSetting='1 day',
            durationStr='1 Y',
            whatToShow='MIDPOINT',
            useRTH=True
        )

    elif ticker_list.loc[Ticker][0] == 'IND':
        contract = Index(symbol=Ticker,
                         exchange=ticker_list.loc[Ticker][1],
                         currency=ticker_list.loc[Ticker][4])
        historical_data = ib.reqHistoricalData(
            contract,
            '',
            barSizeSetting='1 day',
            durationStr='1 Y',
            whatToShow='ADJUSTED_LAST',
            useRTH=True
        )

    dataframe = util.df(historical_data)
    date_n_close = dataframe.iloc[:,[0,4]]
    date = dataframe.date
    close = dataframe.close
    return date_n_close, date, close

# list of all tickers
ticker_list = getTickerlist()

# close data for all tickers in list of all tickers
all_tickers_data = getClose_all_tickers(ticker_list)
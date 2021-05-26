import time
import pandas as pd
import random
import numpy as np
import os
import glob

from ib_insync import *


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

# list of all tickers
ticker_list = getTickerlist()

def getTickers_data(securities_list):
    start_time = time.time()
    date_time = getData(securities_list[0])[1]
    dataframe = pd.DataFrame()
    for i in securities_list:
        date_n_close, date, dataframe[f'{i}_close'], dataframe[f'{i}_volume'] = getData(i)
    dataframe = dataframe.set_index(date_time)
    for column in list(dataframe.columns):
        if 252 > len(dataframe[column].dropna()):
            dataframe = dataframe.drop(columns=[f'{column}'])
            if column[-6:] == '_close':
                data = getData(column[:-6])[0].set_index('date').rename(columns={'close': f'{column}'})
                dataframe = dataframe.join(data, on='date')
            elif column[-7:] == '_volume':
                data = getData(column[:-7])[0].set_index('date').rename(columns={'volume': f'{column}'})
                dataframe = dataframe.join(data, on='date')
    dataframe.interpolate()
    df_close = dataframe.filter(regex='close$', axis=1)
    df_volume = dataframe.filter(regex='volume$', axis=1)
    print("--- %s seconds ---" % (time.time() - start_time))
    return df_close, df_volume

def getSector_performance(securities_list):
    dataframe = pd.DataFrame()
    for i in securities_list:
        dataframe[i] = getData(i)[2]
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

def getData(Ticker):
    path = "dash_project/data"
    all_files = glob.glob(os.path.join(path + "/*.csv"))
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
            durationStr='3 Y',
            whatToShow='MIDPOINT',
            useRTH=True
        )
        dataframe = util.df(historical_data)
        date_n_close = dataframe.iloc[:, [0, 4, 5]]
        date = dataframe.date
        close = dataframe.close
        volume = dataframe.volume
        return date_n_close, date, close, volume

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
            durationStr='3 Y',
            whatToShow='MIDPOINT',
            useRTH=True
        )
        dataframe = util.df(historical_data)
        date_n_close = dataframe.iloc[:, [0, 4, 5]]
        date = dataframe.date
        close = dataframe.close
        volume = dataframe.volume
        return date_n_close, date, close, volume

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
            durationStr='3 Y',
            whatToShow='MIDPOINT',
            useRTH=True
        )
        dataframe = util.df(historical_data)
        date_n_close = dataframe.iloc[:, [0, 4, 5]]
        date = dataframe.date
        close = dataframe.close
        volume = dataframe.volume
        return date_n_close, date, close, volume

    elif ticker_list.loc[Ticker][0] == 'IND':
        contract = Index(symbol=Ticker,
                         exchange=ticker_list.loc[Ticker][1],
                         currency=ticker_list.loc[Ticker][4])
        historical_data = ib.reqHistoricalData(
            contract,
            '',
            barSizeSetting='1 day',
            durationStr='3 Y',
            whatToShow='ADJUSTED_LAST',
            useRTH=True
        )
        dataframe = util.df(historical_data)
        date_n_close = dataframe.iloc[:, [0, 4, 5]]
        date = dataframe.date
        close = dataframe.close
        volume = dataframe.volume
        return date_n_close, date, close, volume

# close data for all tickers in list of all tickers
all_tickers_data, all_tickers_data_volume = getTickers_data(ticker_list)
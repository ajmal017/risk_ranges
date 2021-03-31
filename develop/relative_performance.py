import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib.dates import MonthLocator, DateFormatter

"""
I have to get the dates right, cause at the moment i'm not selecting the data correctly.
- Bitcoin is trading 24/7 and the other metrics are not.
- Currently the CSV files contain 2years of data. Which is why the current selection of data is not correct.
"""
btc = pd.read_csv('./data/BTC-USD.csv')
spy = pd.read_csv('./data/SPY.csv')
gc = pd.read_csv('./data/GLD.csv')
eurusd = pd.read_csv('./data/DX=F.csv')
vix = pd.read_csv('./data/^VIX.csv')
tnx = pd.read_csv('./data/^TNX.csv')
input = pd.read_csv('./data/SLV.csv')

def get_correlation_table(input, btc, gc, eurusd, spy, vix, tnx):
    input = input.loc[:, ['Date', 'Close']].rename(columns={'Close': 'INPUT_Close'})
    btc = btc.loc[:, ['Date', 'Close']].rename(columns={'Close': 'BTC_Close'})
    spy = spy.loc[:, ['Date', 'Close']].rename(columns={'Close': 'SPY_Close'})
    gc = gc.loc[:, ['Date', 'Close']].rename(columns={'Close': 'GC_Close'})
    eurusd = eurusd.loc[:, ['Date', 'Close']].rename(columns={'Close': 'EURUSD_Close'})
    vix = vix.loc[:, ['Date', 'Close']].rename(columns={'Close': 'VIX_Close'})
    tnx = tnx.loc[:, ['Date', 'Close']].rename(columns={'Close': 'TNX_Close'})

    input = input.join(btc.set_index('Date'), on='Date')
    input = input.join(spy.set_index('Date'), on='Date')
    input = input.join(gc.set_index('Date'), on='Date')
    input = input.join(eurusd.set_index('Date'), on='Date')
    input = input.join(vix.set_index('Date'), on='Date')
    input = input.join(tnx.set_index('Date'), on='Date')

    data = input.dropna().set_index('Date')[-252:]
    window = [15, 30, 90, 120]
    list = ['INPUT_Close','BTC_Close', 'SPY_Close', 'GC_Close', 'EURUSD_Close', 'VIX_Close', 'TNX_Close']
    for i in list:
        for x in window:
            data[f'INPUT{i}_{x}'] = data['INPUT_Close'].rolling(x).corr(data[i])
    return data

def rolling_bitcoin_correlation_graph_30d(data):
    data = data.reset_index()
    array = np.array([['INPUTSPY_Close_30', 'black'], ['INPUTEURUSD_Close_30', 'blue'], ['INPUTGC_Close_30', 'grey']])
    list = ['SPY', 'EURUSD', 'GOLD']

    fig = plt.figure(figsize=(15, 7.5))
    ax = fig.add_subplot(111)

    for i, j in array:
        sns.lineplot(x='Date', y=i, data=data, color=j, alpha=.6)
        plt.annotate('%0.2f' % data[i].iloc[-1], xy=(1, data[i].iloc[-1]), xycoords=('axes fraction', 'data'))

    plt.legend(labels=list)
    plt.xlabel('date')
    plt.ylabel('correlation')
    plt.title('30D Rolling Correlations - BTC')
    ax.xaxis.set_major_locator(MonthLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    ax.set_xlim([data['Date'].iloc[0], data['Date'].iloc[-1]])
    ax.set_xticklabels(labels=data.Date.unique(),rotation=25)
    return fig

# plt.show()
# print(rolling_bitcoin_correlation_graph_30d(get_correlation_table(input,btc,gc,eurusd,spy,vix,tnx)))

def get_latestvalue_corr_table(data):
    data_selection = data.iloc[:,11:].reset_index().drop(columns=['Date'])
    days_15 = pd.Series(np.array(data_selection.loc[:, data_selection.columns.to_series().str.contains("15")].tail(1)).reshape(6))
    days_30 = pd.Series(np.array(data_selection.loc[:, data_selection.columns.to_series().str.contains("30")].tail(1)).reshape(6))
    days_90 = pd.Series(np.array(data_selection.loc[:, data_selection.columns.to_series().str.contains("90")].tail(1)).reshape(6))
    days_120 = pd.Series(np.array(data_selection.loc[:, data_selection.columns.to_series().str.contains("120")].tail(1)).reshape(6))
    high_yearly_30_corr = pd.Series(np.array(data_selection.loc[:, data_selection.columns.to_series().str.contains("30")][-252:].max()))
    low_yearly_30_corr = pd.Series(np.array(data_selection.loc[:, data_selection.columns.to_series().str.contains("30")][-252:].min()))

    selection = pd.concat([days_15, days_30, days_90, days_120, high_yearly_30_corr, low_yearly_30_corr], axis=1)
    index = ['BTC','SPY','GC','USD','VIX','10Yr']
    df = pd.DataFrame(selection.values, index=index)
    df = df.rename(columns={0:'15D',
                            1:'30D',
                            2:'90D',
                            3:'120D',
                            4:'1Y 30d High',
                            5:'1Y 30d Low'}).round(2)
    return df



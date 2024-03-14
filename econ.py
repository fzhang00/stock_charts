from datetime import datetime, timedelta
from util import *
import pandas as pd
import sqlite3 as sl
import requests


_con = sl.connect("stock_data.db")
_today = datetime.today()
m6 = timedelta(days=183)

def get_index(start=_today-m6):
    """HSI, NI226, KOSPI, SPX, DJI, IXIC, SOX, STI, 000001-SSE"""
    index_dct = {'^GSPC': 'SP500',
                 '^GSPTSE': 'S&P TSX',
                 '^DJI': 'DowJ' ,
                 '^IXIC': 'NASDAQ',
                 '^HSI': 'HSI',
                 '000001.SS':'SSE',
                #  '^N225': 'Nikkei',
                #  '^STI': 'STI'
                 }
    data = yf.download([key for key,_ in index_dct.items()], start=start)
    close = data['Close']
    close.rename(columns = index_dct, inplace=True)
    close.fillna(method="ffill", inplace=True)
    close.fillna(method="bfill", inplace=True) # in case the first row is nan
    
    return normalize_percent(close, close.columns)

def get_sector_data(start=_today-m6):
    symbols = ['XLC', 'XLY', 'ITB', 'XHB', 'XLP', 'XRT','XLE', 'XOP']
    data = yf.download(symbols, start=start)
    close = data['Close']
    # close.rename(columns = index_dct, inplace=True)
    close.fillna(method="ffill", inplace=True)
    close.fillna(method="bfill", inplace=True) # in case the first row is nan
    
    return normalize_percent(close, close.columns)

def get_job_payroll_dat(start="2020-01-01"):
    """Get 3 employment data that indicate the US Job Market;
        - US Continuing Jobless Claims
        - US Initial Jobless Claims
        - Nonfarm Payroll (yearly change, not done)
        Data normalied by min max. Showing percentage change make more sense. (TODO)
    """
    data = get_fred_data(["CCSA", "ICSA"], start)
    payroll = get_fred_data("PAYEMS", datetime.strptime("2020-01-01", "%Y-%m-%d")-timedelta(days=365))
    data.fillna(method="ffill", inplace=True)
    data.fillna(method="bfill", inplace=True) # in case the first row is nan
    return data

def get_sp_above_avg():
    """MMFI: total stock above 50 days average,
    MMTH: total stock above 200 days average,
    MMOH: total stock above 100 days average,
    MMFI: total stock above 50 days average,
    S5FI : SP500 above 50 days average,
    S5TH : SP500 above 200 days average,
    S5OH : SP500 above 100 days average
    """
    dbdat = pd.read_sql(f"select * from above_avg", _con)
    dat = dbdat.pivot(index='Date', columns='avg_period', values = 'Close')
    dat.rename(columns={p:str(p) for p in dat.columns}, inplace=True)
    dat.index = pd.to_datetime(dat.index, format="%m/%d/%y")
    dat2 = dat.reset_index()
    dat2.sort_values(by='Date', inplace=True)
    dat2.set_index('Date', inplace=True)
    return dat2

def update_sp_above_avg():
    """Scrape SP500 above average data from eoddata.com (last 10 days).
    Add new data into database. Return the entire table. """
    # TODO should make another function for get_sp_above_avg() by just reading the database. 
    # This function should be renamed to download_sp_above_avg()
    table_name = "above_avg"
    sym_dct = {'S5TH':200, 'S5OH':100, 'S5FI':50}
    dat_lst = []
    for sym, p in sym_dct.items():
        url = f'https://www.eoddata.com/stockquote/INDEX/{sym}.htm'
        tables = pd.read_html(url)
        # This is will change with the layout of the webpage
        dat = tables[6] 
        dat['avg_period'] = p
        del(dat['Open Interest'])
        dat_lst.append(dat)
    dat = pd.concat(dat_lst)
    dbdat = pd.read_sql(f"select * from {table_name}", _con)
    merged = pd.merge(dbdat, dat, how = 'outer', indicator=True)
    new = merged.loc[merged._merge == 'right_only']
    # return new
    new.drop(columns=['_merge', 'index'], inplace=True)
    # return new
    new.to_sql(table_name, _con, if_exists='append')


"""
con = sl.connect("stock_data.db")
cur = con.cursor()
cur.execute("CREATE TABLE above_avg(Date, Open, High, Low, Close, Volume)")
"""


def get_ticker_data(symbol, *, rd_csv=False):
    """Get Ticker Data from API. If rd_csv is True, read from ./{ticker}.csv instead"""
    if rd_csv:
        try:
            return pd.read_csv(f'{symbol}.csv')
        except FileNotFoundError:
            print("Cannot fine file {symbol}.csv in current directory.")
            return
        
    """api doc: https://site.financialmodelingprep.com/developer/docs#charts"""
    hist_json = requests.get(f'https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?apikey={_API}').json()

    hist_df = pd.DataFrame(hist_json['historical']).drop('label', axis = 1)
    hist_df = hist_df.iloc[::-1].reset_index().drop(['index','adjClose'], axis = 1)
    hist_df.date = pd.to_datetime(hist_df.date)
    hist_df = hist_df.iloc[:,:6] #.iloc[-365:]
    hist_df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
    return hist_df

def get_sma(df, period : int):
    sma = df.ta.sma(length=period).to_frame()
    sma = sma.reset_index()
    sma['time'] = df['time']
    # sma = sma.rename(columns={f"SMA_{period}": "value"})
    sma = sma.dropna()
    return sma
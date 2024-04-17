import pandas_datareader as web
import pandas as pd
import sqlite3 as sl
import yfinance as yf

from datetime import datetime, timedelta
import colorsys
import glob

def get_hex_color_list(num_colors):
    HSV_tuples = [(x * 1.0 / num_colors, 1, 1) for x in range(num_colors)]
    RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
    hex_codes = [f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}" for r, g, b in RGB_tuples]
    return hex_codes

_TODAY = datetime.today()

def table_exists(con, table):
    cur =con.cursor()
    cur.execte("SELECT name from sqlite_master where type='table' and name='{table}';")
    names = cur.fetchall()
    if names:
        return True
    else:
        return False

def read_db_table(db, table):
    con = sl.connect(db)
    return pd.read_sql(f"select * from '{table}';", con)

# TODO: unfinished
def update_yfinance_data(con, symbol):
    if table_exists(con, symbol):
        dbdat = pd.read_sql(f'select * from "{symbol}"', con)
    return yf.download(symbol)

def get_fred_data(symbols, start, end=_TODAY):
    """Get data from FRED. start and end are in format "YYYY-mm-dd" or datetime"""
    return web.DataReader(symbols,'fred', start, end)


def normalize_minmax(df, column=[]):
    """Normalize a Dataframe column by max()-min() of the last 30 records
    If column not specified, all columns are normalized. """
    if column:
        return (df[column]-df[column].iloc[0])/(df[column].max()-df[column].min())
    else:
        return (df-df.iloc[0])/(df.tail(30).max()-df.tail(30).min())

def normalize_percent(df, column=[]):
    """Normalized a dataset into percentage change reference to the first value. """
    return (df[column]-df[column].iloc[0])/df[column].iloc[0]

def read_eoddata_csv(symbol):
    """Read eoddata csv file into a dataframe."""
    # find downloaded eoddata csv file
    files = glob.glob(f"{symbol.upper()}_*")
    d_lst=[]
    for f in files:
        d_lst.append(pd.read_csv(f, usecols=list(range(1,7)), 
                                 names=['Date', 'Open', 'High', 
                                        'Low', 'Close', 'Volume']))
    a_df = pd.concat(d_lst)
    a_df.Date = pd.to_datetime(a_df.Date)
    a_df = a_df.drop_duplicates()
    return a_df
 
def read_eoddata_total_stock_above_avg():
    """Read Close from total stock above average csv files."""
    symbols = {50:'MMFI', 100:'MMOH', 200:'MMTH'}
    df_dct = {}
    for idx, s in symbols.items():
        df_dct[idx] = read_eoddata_csv(s)[['Date', 'Close']]
    return df_dct
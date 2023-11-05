import pandas_datareader as web
from datetime import datetime

_TODAY_STR = datetime.today()


def get_fred_data(symbols, start, end=_TODAY_STR):
    """Get data from FRED. start and end are in format "YYYY-mm-dd" """
    return web.DataReader(symbols,'fred', start, end)


def normalize_minmax(df, column=[]):
    """Normalize a Dataframe column by its max()-min()"""
    if column:
        return (df[column]-df[column].iloc[0])/(df[column].max()-df[column].min())
    else:
        return (df-df.iloc[0])/(df.tail(30).max()-df.tail(30).min())

def normalize_percent(df, column=[]):
    return (df[column]-df[column].iloc[0])/df[column].iloc[0]

data = get_fred_data("CCSA", "2000-01-01" ,_TODAY_STR)
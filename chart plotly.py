_API = "a839f239d3e2ff7581a77d72aed58821"
from dash import Dash, dcc, html, Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import pandas_ta as ta
import requests
from math import floor
import numpy as np
from econ import *


symbol = '^GSPC'
periods = [20, 60, 120, 240]
rainbow_colors = px.colors.cyclical.mygbm
reds = px.colors.sequential.Reds[3:]
greens = px.colors.sequential.Greens[3:]
bupu = px.colors.sequential.BuPu[3:]
breadth_colors = {50: reds, 100: greens, 200: bupu}



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

def get_sma(df, period : int, idx_name='Date'):
    sma = df.ta.sma(length=period).to_frame()
    sma = sma.reset_index()
    sma[idx_name] = df[idx_name]
    # sma = sma.rename(columns={f"SMA_{period}": "value"})
    sma = sma.dropna()
    return sma

# prep data

# df_close=get_ticker_data(symbol)[['time', 'close']]
df_close = yf.download(symbol, start="2020-01-01")['Close'].reset_index()
melt_cols=['Close']
for p in [5, 10, 20, 60, 120]:
    df_close[f'sma_{p}'] = get_sma(df_close, p)[f'SMA_{p}']
    melt_cols.append(f'sma_{p}')
df_melt = df_close.melt(id_vars=['Date'], value_vars=melt_cols)

breadth = read_eoddata_total_stock_above_avg()
breadth1 = {}
for key, df in breadth.items():
    # melt_breadth = breadth[['Date', 'Close', 'sma_5', 'sma_10', 'sma_20']].melt(id_vars=['Date'], value_vars=['Close', 'sma_5', 'sma_10', 'sma_20'])
    breadth1[key] = df[['Date', 'Close', 'sma_5', 'sma_10', 'sma_20']]


app = Dash(__name__)

app.layout = html.Div([
    html.H4('Live adjustable subplot-width'),
    dcc.Graph(
        id="graph",
        style={"height": "800px"}  # Set the height to 400 pixels
    ),
    html.P("Subplots Width:"),
    dcc.Slider(
        id='slider-width', min=.1, max=.9, 
        value=0.5, step=0.1)
])


@app.callback(
    Output("graph", "figure"), 
    Input("slider-width", "value"))
def customize_width(left_width):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.05, row_heights=[0.7, 0.3])

    # Plot df_close
    c_step = floor(len(rainbow_colors)/len(df_close.columns[1:]))
    for i, column in enumerate(df_close.columns[1:]):
        fig.add_trace(go.Scatter(x=df_close['Date'], y=df_close[column], name=column, line=dict(color=rainbow_colors[i*c_step])), row=1, col=1)

    # Plot breadth data
    for idx, df in breadth1.items():
        for i, column in enumerate(df.columns[1:]):
            fig.add_trace(go.Scatter(x=df['Date'], y=df[column], name=f"above{idx}_"+column, line=dict(color=breadth_colors[idx][i])), row=2, col=1)

    return fig



app.run_server(debug=True)

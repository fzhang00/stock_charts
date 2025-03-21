import dash
from dash import html, dcc, callback, Input, Output
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Register this page
dash.register_page(__name__, path='/market-breadth', name='Market Breadth')

def get_market_data():
    try:
        # Get breadth data from SQLite
        conn = sqlite3.connect('market_data.db')
        symbols = ['S5TH', 'S5OH', 'S5FI', 'MMFI', 'MMOH', 'MMTH']
        
        data = {}
        for symbol in symbols:
            query = f"SELECT date, close FROM symbol_{symbol} ORDER BY date"
            df = pd.read_sql_query(query, conn)
            if not df.empty:
                # Convert 'date' column to datetime objects
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                data[symbol] = df['close']
        
        conn.close()
        
        # Get SP500 data
        try:
            sp500 = yf.download('^GSPC', start='2020-01-01', progress=False)
            if not sp500.empty:
                sp500_series = sp500['Close']
                # Convert index to datetime objects (already is, but for clarity)
                sp500_series.index = pd.to_datetime(sp500_series.index)
                logging.info(f"Successfully downloaded S&P 500 data, length: {len(sp500_series)}")
            else:
                logging.error("Downloaded S&P 500 data is empty")
                sp500_series = None
        except Exception as e:
            logging.error(f"Error downloading S&P 500 data: {e}")
            sp500_series = None
        
        return data, sp500_series
    
    except Exception as e:
        logging.error(f"Error in get_market_data: {e}")
        return {}, None

# Layout
layout = html.Div([
    html.H2('Market Breadth Indicators'),
    html.P('Showing percentage of stocks above moving averages'),
    dcc.Graph(id='market-breadth-plot')
])

@callback(
    Output('market-breadth-plot', 'figure'),
    Input('market-breadth-plot', 'id')
)
def update_breadth_plot(_):
    breadth_data, sp500 = get_market_data()
    
    # Create figure with subplots
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.05,
                        subplot_titles=('% Stocks Above MA', 'S&P 500'))

    
    # Add breadth traces
    colors = {
        'S5TH': '#FF0000',  # SP500 200d
        'S5OH': '#FFA500',  # SP500 50d
        'S5FI': '#008000',  # SP500 5d
        'MMTH': '#0000FF',  # NASDAQ 200d
        'MMOH': '#4B0082',  # NASDAQ 50d
        'MMFI': '#800080'   # NASDAQ 5d
    }
    
    descriptions = {
        'S5TH': 'S&P500 Above 200d MA',
        'S5OH': 'S&P500 Above 50d MA',
        'S5FI': 'S&P500 Above 5d MA',
        'MMTH': 'MARKET Above 200d MA',
        'MMOH': 'MARKET Above 50d MA',
        'MMFI': 'MARKET Above 5d MA'
    }
    
    for symbol, data in breadth_data.items():
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data,
                name=descriptions[symbol],
                line=dict(color=colors[symbol])
            ),
            row=1, col=1  # Add to the first subplot (top)
        )
    
    # Add SP500 trace if data is available
    print("data type", type(data))
    print("sp500 type", type(sp500))
    if sp500 is not None and not sp500.empty:
        for symbol, data in sp500.items():
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data,
                    name='S&P 500',
                    line=dict(color='black', dash='dash')
                ),
                row=2, col=1  # Add to the second subplot (bottom)
            )
    
    # Update layout
    fig.update_layout(
        title='Market Breadth vs S&P 500',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.05
        ),
        width=1200,
        height=800,  # Increased height for two subplots
        margin=dict(r=200)
    )

    fig.update_yaxes(title_text="% Stocks Above MA", row=1, col=1)
    fig.update_yaxes(title_text="S&P 500", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1) # x-axis title on bottom plot

    
    return fig 
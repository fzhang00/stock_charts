import datetime
import pandas_datareader as web
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import numpy as np

# Data fetching and preparation
today = datetime.datetime.today()
start_date = datetime.datetime(2000,1,1)

yield_t = ['DGS1MO', 'DGS6MO', 'DGS1', 'DGS2', 'DGS5', 'DGS10', 'DGS20']
durations = [1/12, 0.5, 1, 2, 5, 10, 20]  # Convert all terms to years
yield_t_df = web.DataReader(yield_t,'fred', start_date, today)
yield_t_df = yield_t_df.ffill()  # Clean NaN values

idx_smp = [-1, -3, -20, -60, -120, -260]  # Sample points from recent to old
rainbow_colors = ['#FF0000', '#FFA500', '#008000', '#0000FF', '#4B0082', '#800080']

# Initialize Dash app
app = Dash(__name__)

# Layout
app.layout = html.Div([
    html.H2('US Treasury Yield Curves'),
    html.P('Showing yield curves at different time points'),
    
    # Date display
    html.H3(id='date-display'),
    
    # Slider with updatemode='drag'
    dcc.Slider(
        id='time-slider',
        min=abs(min(idx_smp)),
        max=len(yield_t_df) - 1,
        value=len(yield_t_df) - 1,
        step=1,
        updatemode='drag',  # Update while dragging
        marks={i: yield_t_df.index[i].strftime('%Y-%m-%d') 
               for i in range(0, len(yield_t_df), len(yield_t_df)//10)},
        tooltip={"placement": "bottom", "always_visible": True}  # Add tooltip for current value
    ),
    
    # Plot
    dcc.Graph(id='yield-curves-plot')
], style={'margin': '20px', 'maxWidth': '1200px'})

@app.callback(
    [Output('yield-curves-plot', 'figure'),
     Output('date-display', 'children')],
    [Input('time-slider', 'value')]
)
def update_figure(time_index):
    idx = int(time_index)
    reference_date = yield_t_df.index[idx]
    
    # Create figure
    fig = go.Figure()
    
    # Add curves
    for offset, color in zip(idx_smp, rainbow_colors):
        target_idx = idx + offset
        if target_idx >= 0 and target_idx < len(yield_t_df):
            curve_data = yield_t_df.iloc[target_idx]
            date_str = yield_t_df.index[target_idx].strftime('%Y-%m-%d')
            days_diff = abs((reference_date - yield_t_df.index[target_idx]).days)
            
            label = f"{date_str} (Current)" if offset == -1 else f"{date_str} ({days_diff} days ago)"
            
            fig.add_trace(go.Scatter(
                x=durations,
                y=curve_data,
                name=label,
                line=dict(color=color, width=2)
            ))
    
    # Update layout
    fig.update_layout(
        title='US Treasury Yield Curves',
        xaxis_title='Duration (Years)',
        yaxis_title='Yield (%)',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.05
        ),
        width=800,
        height=500,
        margin=dict(r=200)  # Add right margin for legend
    )
    
    date_display = f"Current reference date: {reference_date.strftime('%Y-%m-%d')}"
    
    return fig, date_display

if __name__ == '__main__':
    app.run_server(debug=True)
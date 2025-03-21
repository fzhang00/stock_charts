import dash
from dash import html, dcc, callback, Input, Output
import datetime
import pandas_datareader as web
import plotly.graph_objects as go
import numpy as np

# Register this page
dash.register_page(__name__, path='/', name='Yield Curves')

# Add variables to track data fetching
last_fetch_time = None
yield_t_df = None

# Keep your existing fetch_yield_data function
# ... (copy the function from your original code)

def fetch_yield_data():
    global last_fetch_time, yield_t_df
    try:
        today = datetime.datetime.today()
        start_date = datetime.datetime(2000,1,1)
        
        yield_t = ['DGS1MO', 'DGS6MO', 'DGS1', 'DGS2', 'DGS5', 'DGS10', 'DGS20']
        durations = [1/12, 0.5, 1, 2, 5, 10, 20]  # Convert all terms to years
        
        new_df = web.DataReader(yield_t,'fred', start_date, today)
        new_df = new_df.ffill()  # Clean NaN values
        
        # Only update global variables if fetch was successful
        yield_t_df = new_df
        last_fetch_time = datetime.datetime.now()
        return yield_t_df, durations
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        # If we already have data, keep using it
        if yield_t_df is not None:
            return yield_t_df, durations
        else:
            raise  # Re-raise the exception if we have no existing data

# Initial data fetch
yield_t_df, durations = fetch_yield_data()

idx_smp = [-1, -3, -20, -60, -120, -260]
rainbow_colors = ['#FF0000', '#FFA500', '#008000', '#0000FF', '#4B0082', '#800080']

# Layout
layout = html.Div([
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
        updatemode='drag',
        marks={i: yield_t_df.index[i].strftime('%Y-%m-%d') 
               for i in range(0, len(yield_t_df), len(yield_t_df)//10)},
        tooltip={"placement": "bottom", "always_visible": True}
    ),
    
    # Plot
    dcc.Graph(id='yield-curves-plot')
], style={'maxWidth': '1600px'})

# Keep your existing callback
@callback(
    [Output('yield-curves-plot', 'figure'),
     Output('date-display', 'children')],
    [Input('time-slider', 'value')]
)
def update_figure(time_index):
    global last_fetch_time, yield_t_df
    
    # Check if we need to refetch data (more than 24 hours since last fetch)
    current_time = datetime.datetime.now()
    if last_fetch_time and (current_time - last_fetch_time).total_seconds() > 24 * 3600:
        try:
            yield_t_df, _ = fetch_yield_data()
        except Exception as e:
            print(f"Failed to refresh data: {e}")
            # Continue with existing data
            pass
    
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
        width=1200,
        height=600,
        margin=dict(r=200)  # Add right margin for legend
    )
    
    date_display = f"Current reference date: {reference_date.strftime('%Y-%m-%d')}"
    
    return fig, date_display

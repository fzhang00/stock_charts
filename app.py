from dash import Dash, html, dcc
import dash

app = Dash(
    __name__, 
    use_pages=True,
    suppress_callback_exceptions=True,
    prevent_initial_callbacks=True
)

app.layout = html.Div([
    # Left side menu
    html.Div([
        html.H2('Market Analysis', style={'textAlign': 'center'}),
        html.Hr(),
        dcc.Link('Yield Curves', href='/'),
        html.Br(),
        html.Br(),
        dcc.Link('Market Breadth', href='/market-breadth'),
    ], style={
        'width': '200px',
        'float': 'left',
        'height': '100vh',
        'borderRight': '1px solid #ccc',
        'padding': '20px'
    }),
    
    # Main content area
    html.Div([
        dash.page_container
    ], style={
        'marginLeft': '240px',
        'padding': '20px'
    })
])

if __name__ == '__main__':
    app.run_server(
        debug=True,
        dev_tools_hot_reload=False
    ) 
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
        ],
        value='ALL',
        placeholder='Select a Launch Site',
        searchable=True
    ),
    
    html.Br(),
    
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),
    
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for success pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Calculate the success rate for each site
        site_success = spacex_df.groupby(['Launch Site', 'class']).size().unstack(fill_value=0)
        site_success['Total'] = site_success[0] + site_success[1]
        site_success['Success Rate'] = site_success[1] / site_success['Total'] * 100

        # Create a DataFrame for plotting
        df = site_success[['Success Rate']].reset_index()
        df = df.rename(columns={'Success Rate': 'Success Rate (%)'})
        
        fig = px.pie(
            df,
            names='Launch Site',
            values='Success Rate (%)',
            title='Total Success Rate by Launch Site'
        )
    else:
        # Filter for the selected site
        df = spacex_df[spacex_df['Launch Site'] == selected_site]
        df = df.groupby('class').size().reset_index(name='count')

        fig = px.pie(
            df,
            values='count',
            names='class',
            title=f'Launch Success Count for {selected_site}'
        )
    
    return fig

# Callback for scatter plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def update_scatter_plot(selected_site, payload_range):
    min_payload, max_payload = payload_range
    
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= min_payload) & 
                            (spacex_df['Payload Mass (kg)'] <= max_payload)]
    
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    fig = px.scatter(
        filtered_df, 
        x='Payload Mass (kg)', 
        y='class',
        color='Booster Version Category',
        title='Payload vs. Success Scatter Plot',
        labels={'class': 'Launch Success (1=Success, 0=Failure)'}
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
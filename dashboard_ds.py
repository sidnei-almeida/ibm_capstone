import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import wget

# Download the dataset if it doesn't exist
try:
    spacex_df = pd.read_csv('spacex_launch_dash.csv')
except FileNotFoundError:
    url = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv'
    wget.download(url)
    spacex_df = pd.read_csv('spacex_launch_dash.csv')

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Initialize the app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# Create the app layout using Bootstrap components
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1('SpaceX Launch Records Dashboard',
                        className='text-center text-primary, mb-4'),
                width=12)
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='site-dropdown',
                options=[
                    {'label': 'All Sites', 'value': 'ALL'},
                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                ],
                value='ALL',
                placeholder="Select a Launch Site",
                searchable=True,
                className='mb-3'
            ),
            html.P("Payload Mass Range (Kg):"),
            dcc.RangeSlider(
                id='payload-slider',
                min=0, max=10000, step=1000,
                marks={i: f'{i}' for i in range(0, 10001, 2500)},
                value=[min_payload, max_payload]
            ),
        ], width=12),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='success-pie-chart'), width=12, md=6),
        dbc.Col(dcc.Graph(id='success-payload-scatter-chart'), width=12, md=6),
    ])
], fluid=True)

# Callback for the pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(
            spacex_df[spacex_df['class'] == 1],
            names='Launch Site',
            title='<b>Total Successful Launches by Site</b>',
            template='plotly_dark'
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        site_df = filtered_df['class'].value_counts().reset_index()
        site_df.columns = ['class', 'count']
        fig = px.pie(
            site_df,
            values='count',
            names='class',
            title=f'<b>Success vs. Failure for {entered_site}</b>',
            template='plotly_dark',
            color='class',
            color_discrete_map={1: '#42f56c', 0: '#f54242'} # Green for success, Red for failure
        )
    fig.update_layout(transition_duration=500)
    return fig

# Callback for the scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]

    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='<b>Payload vs. Outcome for All Sites</b>',
            template='plotly_dark'
        )
    else:
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'<b>Payload vs. Outcome for {entered_site}</b>',
            template='plotly_dark'
        )
    fig.update_layout(transition_duration=500)
    return fig

# Run the app
if __name__ == '__main__':
    app.run()
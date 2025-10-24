# Importing necessary libraries
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from dash import no_update
import datetime as dt

# Import dataset
data='spacex_launch_dash.csv'
df=pd.read_csv(data)
df.drop('Unnamed: 0', axis=1, inplace=True)
max_payload = df['Payload Mass (kg)'].max()
min_payload = df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=[{'label': 'All Sites', 'value':'All Sites'},
                                                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                    {'label': 'VAFB SLC-4E',  'value': 'VAFB SLC-4E'},
                                                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}],
                                            value='All Sites', placeholder='Select a Launch Site Here', searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                               min=0,
                                                max=10000,
                                               step=1000,
                                               value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
             Input(component_id='site-dropdown', component_property='value'))

# Define function to return pie chart
def get_pie_chart(entered_site):
    data=df.groupby('Launch Site')['class'].mean().reset_index()
    if entered_site=='All Sites':
        fig1=px.pie(data, values='class', names='Launch Site', title='Success rate for all sites')
        fig1.update_layout(legend_title_text='Launch Site')
        return fig1
    elif entered_site in data['Launch Site'].unique():
        filtered_data=df[df['Launch Site']==entered_site]
        class_count=filtered_data['class'].value_counts().reset_index()
        class_count.columns=['class', 'count']
        class_count['class']=class_count['class'].map({1: 'Success', 0: 'Failure'})
        fig2=px.pie(class_count, values='count', names='class', title=f'Success rate for {entered_site}')
        
        # Customize legend
        fig2.update_layout(
    legend_title_text='Launch Outcome',
    legend=dict(
        orientation='v',
        x=1.05,
        y=1,
        font=dict(size=12, color='black')
    )
)

        return fig2

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
             [Input(component_id='site-dropdown', component_property='value'),
              Input(component_id='payload-slider', component_property='value')]
    
)

# Define a function to generate scatter plot
def get_scatter_plot(entered_site, payload_range):
    low, high = payload_range
    filtered_df = df[(df['Payload Mass (kg)'] >= low) & (df['Payload Mass (kg)'] <= high)]

    if entered_site == 'All Sites':
        fig3 = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version',
            title='Correlation between Payload Mass and Success Rate for All Sites'
        )
        return fig3
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig4 = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version',
            title=f'Correlation between Payload and Success Rate for {entered_site}'
        )
        return fig4

# Run the app
if __name__ == '__main__':
    app.run()
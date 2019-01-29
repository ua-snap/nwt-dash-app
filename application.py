"""
NWT Mine site future climate tool
"""
# pylint: disable=invalid-name, import-error, line-too-long, too-many-arguments
import os
import json
import pickle
import itertools
import plotly.graph_objs as go
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import picnic_css_dash_components as pcdc

with open('data.pickle', 'rb') as handle:
    data = pickle.load(handle)

# data prep for initial display
df = data[1]['tas']
pts = pd.read_csv('minesites.csv', index_col=0)
mapbox_access_token = os.environ['MAPBOX_ACCESS_TOKEN']
scenarios = ['rcp45', 'rcp60', 'rcp85']

map_traces = [
    go.Scattermapbox(
        lat=pts.loc[:, 'Latitude'],
        lon=pts.loc[:, 'Longitude'],
        mode='markers',
        marker=dict(
            size=15,
            color='rgb(140,86,75)'
        ),
        line={
            'color': 'rgb(0, 0, 0)',
            'width': 2
        },
        text=pts.loc[:, 'Name'],
        hoverinfo='text'
    )
]

map_layout = go.Layout(
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        zoom=3.5,
        center=dict(lat=64, lon=-116.6),
        layers=[
            dict(
                sourcetype='geojson',
                source=json.loads(open('./NorthwestTerritories_4326.geojson', 'r').read()),
                type='fill',
                color='rgba(255,0,0,0.1)'
            )
        ]
    ),
    showlegend=False,
    margin=dict(l=0, r=0, t=0, b=0)
)

map_figure = go.Figure({
    'data': map_traces,
    'layout': map_layout
})

# LINE COLORS LOOKUP -- hacky but somewhat working
ms_colors = {
    'GISS-E2-R': {'rcp45': '#FDD017', 'rcp60': '#F2BB66', 'rcp85': '#EAC117'},
    'GFDL-CM3': {'rcp45': '#6AA121', 'rcp60': '#347C17', 'rcp85': '#254117'},
    '5ModelAvg': {'rcp45': '#736F6E', 'rcp60': '#463E3F', 'rcp85': '#2B1B17'},
    'IPSL-CM5A-LR': {'rcp45': '#C24641', 'rcp60': '#7E3517', 'rcp85': '#800517'},
    'MRI-CGCM3': {'rcp45': '#4863A0', 'rcp60': '#2B547E', 'rcp85': '#151B54'},
    'NCAR-CCSM4': {'rcp45': '#C35817', 'rcp60': '#6F4E37', 'rcp85': '#493D26'}
}

app = dash.Dash(__name__)
# Beanstalk looks for application by default, if this isn't set you will get a WSGI error.
application = app.server

app.title = 'NWT Climate Scenarios Explorer'

form_fields = [
    html.Div(
        className='region-selector form--wrapper',
        children=[
            dcc.Dropdown(
                id='minesites-dropdown',
                options=[
                    {
                        'label': i.replace('_', ' '),
                        'value': i
                    } for i in df.minesite.unique()
                ],
                value='Prairie_Creek_Mine',
                multi=False,
            ),
            html.Span('or', className='form--inline--text'),
            pcdc.PChecklist(
                id='if-mine-site',
                className='form--inline--text',
                label='if-mine-site',
                options=[
                    {'label': 'Territory', 'value': 'territory'}
                ],
                values=[]
            )
        ]
    ),

    html.Div(className='form--wrapper', children=[
        html.Label(
            'Scenario(s):',
            className='form--inline'
        ),
        pcdc.PChecklist(
            id='scenario-check',
            label='scenario',
            options=[
                {'label':'RCP4.5', 'value':'rcp45'},
                {'label':'RCP6.0', 'value':'rcp60'},
                {'label':'RCP8.5', 'value':'rcp85'}
            ],
            values=['rcp85'],
            labelStyle={'display': 'inline-block'},
            className='form--inline'
        ),
    ]),
    html.Div(className='form--wrapper', children=[
        pcdc.PRadios(
            id='variable-toggle',
            options=[
                {'label': 'Temperature', 'value':'tas'},
                {'label': 'Precipitation', 'value':'pr'}
            ],
            value='tas'
        )
    ]),
    html.Div(
        id='month-div',
        className='form--wrapper',
        children=[
            pcdc.PChecklist(
                id='all-month-check',
                label='all-month-check',
                options=[
                    {'label': 'All months', 'value': 'all'}],
                values=[],
            ),
            dcc.Dropdown(
                id='month-dropdown',
                options=[
                    {'label': 'January', 'value': '1'},
                    {'label': 'February', 'value': '2'},
                    {'label': 'March', 'value': '3'},
                    {'label': 'April', 'value': '4'},
                    {'label': 'May', 'value': '5'},
                    {'label': 'June', 'value': '6'},
                    {'label': 'July', 'value': '7'},
                    {'label': 'August', 'value': '8'},
                    {'label': 'September', 'value': '9'},
                    {'label': 'October', 'value': '10'},
                    {'label': 'November', 'value': '11'},
                    {'label': 'December', 'value': '12'}
                ],
                value=[1],
                multi=True,
                disabled=False
            )
        ]
    ),

    html.Div(className='form--wrapper', children=[
        html.Label(
            'Model(s)'
        ),
        dcc.Dropdown(
            id='model-dropdown',
            options=[{'label': i, 'value': i}
                     for i in df.model.unique()],
            value=['IPSL-CM5A-LR'],
            multi=True
        )
    ]),

    dcc.Graph(id='minesites-map', figure=map_figure, config={'displayModeBar': False})
]

# # BUILD PAGE LAYOUT
app.layout = html.Div(
    className='flex three demo app-wrapper',
    children=[
        html.H1('Northwest Territories Climate Scenarios Explorer', className="full"),

        html.Div(
            id='leftcol',
            className='column',
            children=form_fields
        ),

        # Right column
        html.Div(
            className="two-third column",
            children=[
                dcc.Graph(id='my-graph'),
                dcc.RangeSlider(
                    id='range-slider',
                    marks={str(year): str(year)
                           for year in df['year'].unique()[::2]},
                    min=df['year'].min(),
                    max=df['year'].max(),
                    step=1,
                    value=[
                        df['year'].unique().min(),
                        df['year'].unique().max()
                    ],
                )
            ]
        )
    ]
)

def average_months(dff, model, scenario, variable_value):
    '''
    in case of multiple months allowed to be chosen
    average all of the months together to single traces.
    '''
    sub_df = dff[(dff['model'] == model) & (dff['scenario'] == scenario)]
    dfm = sub_df.groupby('month').apply(
        lambda x: x[variable_value].reset_index(
            drop=True)
        ).T.mean(
            axis=1
        ).copy()
    # convert back to a DataFrame from the output Series...
    dfm = dfm.to_frame(name=variable_value).reset_index(drop=True)
    dfm['year'] = sub_df['year'].unique()
    dfm['model'] = model
    dfm['scenario'] = scenario
    dfm['month'] = '_'.join(['avg'] + [str(m) for m in dff.month.unique()])
    return dfm

@app.callback(
    Output('minesites-dropdown', 'disabled'),
    [Input('if-mine-site', 'values')]
)
def disable_mine_sites(values):
    """ Disable mine site selector when "Entire Territory" is selected """
    return True if values else False

@app.callback(
    Output('month-dropdown', 'disabled'),
    [Input('all-month-check', 'values')]
)
def disable_month_dropdown(values):
    """ Disable months selector when "All months" is selected """
    return True if values else False

@app.callback(
    Output('minesites-dropdown', 'value'),
    [
        Input('minesites-map', 'clickData'),
        Input('if-mine-site', 'values')
    ]
)
def update_mine_site_dropdown(selected_on_map, values):
    """ If user clicks on the map, update the drop down. """
     # if "territory-wide" is checked, ignore map clicks
    if 'territory' in values:
        return None
    if selected_on_map is not None:
        return selected_on_map['points'][0]['text'].replace(' ', '_')
    # Return a default
    return 'Prairie_Creek_Mine'

@app.callback(
    Output('my-graph', 'figure'),
    [
        Input('if-mine-site', 'values'),
        Input('minesites-dropdown', 'value'),
        Input('range-slider', 'value'),
        Input('scenario-check', 'values'),
        Input('model-dropdown', 'value'),
        Input('month-dropdown', 'value'),
        Input('all-month-check', 'values'),
        Input('variable-toggle', 'value'),
        Input('minesites-map', 'clickData')
    ]
)
def update_graph(
    if_mine_site,
    minesite,
    year_range,
    scenario_values,
    model_values,
    months,
    all_check,
    variable_value,
    selected_on_map):
    """ Update graph from UI controls """
    region_value = 2 if 'territory' in if_mine_site else 1

    cur_df = data[region_value][variable_value].copy()
    if 'group' in cur_df.columns:
        cur_df = cur_df.drop('group', axis=1)

    if region_value == 1:
        dff = cur_df[(cur_df.minesite == minesite)].copy()
    else:
        dff = cur_df.copy()

    begin_range, end_range = year_range
    dff = dff[(dff['year'] >= begin_range) & (dff['year'] <= end_range)]
    dff = dff.loc[dff['scenario'].isin(scenario_values), ]
    dff = dff.loc[dff['model'].isin(model_values), ]

    # months
    if 'all' in all_check:
        months = list(range(1, 12 + 1))

    dff = dff.loc[dff['month'].isin(months), ]

    if len(dff.month.unique()) > 1:
        dff = pd.concat([average_months(dff, m, s, variable_value) for m, s in itertools.product(
            dff.model.unique(), dff.scenario.unique())], axis=0)

    dff = dff.reset_index(drop=True)

    if 'all' in all_check:
        title_lu = {
            'tas': 'Decadal Annual Mean Temperatures',
            'pr': 'Decadal Annual Mean Precipitation'
        }
        title = title_lu[variable_value]
    else:
        title_lu = {
            'tas': 'Decadal Monthly Mean Temperatures',
            'pr': 'Decadal Monthly Mean Precipitation'
        }
        title = title_lu[variable_value]

    yaxis_title = {
        'tas': 'Degrees Celcius',
        'pr': 'millimeters'
    }

    return {
        'data': [
            go.Scatter(
                x=j['year'],
                y=j[variable_value],
                name=i[0] + ' ' + i[1],
                line=dict(color=ms_colors[i[0]][i[1]], width=2),
                mode='lines'
            ) for i, j in dff.groupby(['model', 'scenario', 'month'])
        ],
        'layout': {
            'title': title,
            'xaxis': dict(title='Decades'),
            'yaxis': dict(title=yaxis_title[variable_value])
        }
    }


if __name__ == '__main__':
    application.run(debug=True, port=8080)

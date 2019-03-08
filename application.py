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

with open('data.pickle', 'rb') as handle:
    data = pickle.load(handle)

# data prep for initial display
df = data[1]['tas']
pts = pd.read_csv('minesites.csv', index_col=0)
mapbox_access_token = os.environ['MAPBOX_ACCESS_TOKEN']

# Lookup tables for a few things used in form inputs & graph title
variables_lut = {
    'tas': 'Temperature',
    'pr': 'Precipitation'
}

scenarios_lut = {
    'rcp45': 'RCP 4.5',
    'rcp60': 'RCP 6.0',
    'rcp85': 'RCP 8.5',
}

months_lut = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}

models_lut = {
    'GISS-E2-R': 'GISS-E2-R',
    'GFDL-CM3': 'GFDL-CM3',
    '5ModelAvg': 'Five Model Average',
    'IPSL-CM5A-LR': 'IPSL-CM5A-LR',
    'MRI-CGCM3': 'MRI-CGCM3',
    'NCAR-CCSM4': 'NCAR-CCSM4'
}

map_traces = [
    go.Scattermapbox(
        lat=pts.loc[:, 'Latitude'],
        lon=pts.loc[:, 'Longitude'],
        mode='markers',
        marker={
            'size': 15,
            'color': 'rgb(140,86,75)'
        },
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
# AWS Elastic Beanstalk looks for application by default,
# if this variable (application) isn't set you will get a WSGI error.
application = app.server
app.title = 'NWT Climate Scenarios Explorer'

# We want this HTML structure to get the full-width background color:
# <div class="header">
#   <div class="container"> gives us the centered column
#     <div class="section"> a bit more padding to stay consistent with form
header_section = html.Div(
    className='header',
    children=[
        html.Div(
            className='container',
            children=[
                html.Div(
                    className='section',
                    children=[
                        html.Div(
                            className='header--logo',
                            children=[
                                html.A(
                                    className='header--snap-link',
                                    children=[
                                        html.Img(src='assets/SNAP.svg')
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            className='header--titles',
                            children=[
                                html.H1(
                                    'Northwest Territories Climate Scenarios Explorer',
                                    className='title is-2'
                                ),
                                html.H2(
                                    'See temperature and precipitation projections for selected NWT locations under various climate scenarios, from now until far into the future.',
                                    className='subtitle is-4'
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

footer = html.Footer(
    className='footer has-text-centered',
    children=[
        html.Div(
            children=[
                html.A(
                    href='https://snap.uaf.edu',
                    target='_blank',
                    className='level-item',
                    children=[
                        html.Img(
                            src='assets/SNAP.svg'
                        )
                    ]
                ),
                html.A(
                    href='https://uaf.edu/uaf/',
                    target='_blank',
                    className='level-item',
                    children=[
                        html.Img(
                            src='assets/UAF.svg'
                        )
                    ]
                ),
                html.A(
                    href='https://www.gov.nt.ca/',
                    target='_blank',
                    className='level-item',
                    children=[
                        html.Img(
                            src='assets/NWT.svg'
                        )
                    ]
                )
            ]
        ),
        dcc.Markdown(
            """
This tool is part of an ongoing collaboration between SNAP and the Government of Northwest Territories. We are working to make a wide range of downscaled climate products that are easily accessible, flexibly usable, and fully interpreted and understandable to users in the Northwest Territories, while making these products relevant at a broad geographic scale.

UA is an AA/EO employer and educational institution and prohibits illegal discrimination against any individual. [Statement of Nondiscrimination](https://www.alaska.edu/nondiscrimination/)
            """,
            className='content is-size-5'
        )
    ]
)

minesites_dropdown_field = html.Div(
    className='field',
    children=[
        html.Label('Location', className='label'),
        html.Div(className='control', children=[
            dcc.Dropdown(
                id='minesites-dropdown',
                options=[
                    {
                        'label': i.replace('_', ' '),
                        'value': i
                    } for i in df.minesite.unique()
                ],
                value='Prairie_Creek_Mine'
            )
        ])
    ]
)

scenarios_checkbox_field = html.Div(
    className='field',
    children=[
        html.Label('Scenario(s)', className='label'),
        dcc.Checklist(
            labelClassName='checkbox',
            className='control',
            id='scenario-check',
            options=list(
                map(
                    lambda k: {
                        'label': scenarios_lut[k],
                        'value': k
                    }, scenarios_lut
                )
            ),
            values=['rcp85']
        )
    ]
)

variable_toggle_field = html.Div(
    className='field',
    children=[
        html.Label('Variable', className='label'),
        dcc.RadioItems(
            labelClassName='radio',
            className='control',
            id='variable-toggle',
            options=list(
                map(
                    lambda k: {
                        'label': variables_lut[k],
                        'value': k
                    }, variables_lut
                )
            ),
            value='tas'
        )
    ]
)

months_field = html.Div(
    className='field',
    children=[
        html.Label('Months', className='label'),
        dcc.Checklist(
            labelClassName='checkbox',
            className='control',
            id='all-month-check',
            options=[
                {'label': ' All months', 'value': 'all'}],
            values=[]
        ),
        html.Div(className='control', children=[
            dcc.Dropdown(
                id='month-dropdown',
                options=list(
                    map(
                        lambda k: {
                            'label': months_lut[k],
                            'value': k
                        }, months_lut
                    )
                ),
                value=[1],
                multi=True,
                disabled=False
            )
        ])
    ]
)

models_field = html.Div(
    className='field',
    children=[
        html.Label('Models(s)', className='label'),
        dcc.Dropdown(
            id='model-dropdown',
            options=[{'label': i, 'value': i}
                     for i in df.model.unique()],
            value=['IPSL-CM5A-LR'],
            multi=True
        )
    ]
)

form_fields = html.Div(
    className='columns form',
    children=[
        html.Div(
            className='column is-two-thirds',
            children=[
                html.H3(
                    'Step 1: Choose a location using the list or map.',
                    className='title is-5'
                ),
                minesites_dropdown_field,
                dcc.Graph(
                    id='minesites-map',
                    figure=map_figure,
                    config={
                        'displayModeBar': False
                    }
                )
            ]
        ),
        html.Div(
            className='column',
            children=[
                html.H3(
                    'Step 2: Choose variables.',
                    className='title is-5'
                ),
                scenarios_checkbox_field,
                variable_toggle_field,
                months_field,
                models_field
            ]
        )
    ]
)

main_layout = html.Div(
    className='container',
    children=[
        html.Div(
            className='section',
            children=[
                form_fields,
            ]
        ),
        html.Div(
            className='section graph',
            children=[
                dcc.Graph(id='my-graph'),
                dcc.RangeSlider(
                    id='range-slider',
                    marks={i: i for i in range(2000, 2320, 20)},
                    min=2000,
                    max=2300,
                    step=20,
                    value=[
                        2000,
                        2300
                    ]
                )
            ]
        )
    ]
)

app.layout = html.Div(
    children=[
        header_section,
        main_layout,
        footer
    ]
)

def build_plot_title(location, variable, start, end, annual, months, scenarios, models):
    ''' Return a string containing the map title '''
    from pprint import pprint
    pprint(months)
    def join_strings_with_commas(lut, items):
        return ', '.join(list(map(lambda k: lut[k], items))).rstrip(', ')

    title = location + '<br>'
    if annual:
        title += 'Decadal Annual Mean '
        months_fragment = ''
    else:
        title += 'Decadal Monthly Mean '
        months.sort()
        months_fragment = '<br>' +  join_strings_with_commas(months_lut, months)

    title += variables_lut[variable] + ', ' + str(start) + '-' + str(end) + months_fragment

    scenarios.sort()
    models.sort()

    title += '<br>' + join_strings_with_commas(scenarios_lut, scenarios)
    title += '<br>' + join_strings_with_commas(models_lut, models)

    return title

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
    Output('month-dropdown', 'disabled'),
    [Input('all-month-check', 'values')]
)
def disable_month_dropdown(values):
    """ Disable months selector when "All months" is selected """
    return bool(values)

@app.callback(
    Output('minesites-dropdown', 'value'),
    [
        Input('minesites-map', 'clickData')
    ]
)
def update_mine_site_dropdown(selected_on_map):
    """ If user clicks on the map, update the drop down. """
     # if "territory-wide" is checked, ignore map clicks
    if selected_on_map is not None:
        return selected_on_map['points'][0]['text'].replace(' ', '_')
    # Return a default
    return 'Prairie_Creek_Mine'

@app.callback(
    Output('my-graph', 'figure'),
    [
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
    minesite,
    year_range,
    scenario_values,
    model_values,
    months,
    all_check,
    variable_value,
    selected_on_map):
    """ Update graph from UI controls """
    region_value = 1

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

    title = build_plot_title(minesite, variable_value, begin_range, end_range, all_check, months, scenario_values, model_values)

    yaxis_title = {
        'tas': 'Degrees Celsius',
        'pr': 'Millimeters'
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
            'xaxis': dict(title='Year'),
            'yaxis': dict(title=yaxis_title[variable_value])
        }
    }


if __name__ == '__main__':
    application.run(debug=True, port=8080)

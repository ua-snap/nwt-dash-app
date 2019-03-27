"""
NWT Mine site future climate tool
"""
# pylint: disable=invalid-name, import-error, line-too-long, too-many-arguments
import os
import json
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

communities = pd.read_pickle('community_places.pickle')
mapbox_access_token = os.environ['MAPBOX_ACCESS_TOKEN']
path_prefix = os.environ['REQUESTS_PATHNAME_PREFIX']

# Google analytics tag
gtag_id = os.environ['GTAG_ID']

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
        lat=communities.loc[:, 'latitude'],
        lon=communities.loc[:, 'longitude'],
        mode='markers',
        marker={
            'size': 15,
            'color': 'rgb(140,86,75)'
        },
        line={
            'color': 'rgb(0, 0, 0)',
            'width': 2
        },
        text=communities.index,
        hoverinfo='text'
    )
]

map_layout = go.Layout(
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        zoom=3,
        center=dict(lat=68, lon=-120),
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
                    className='section header--section',
                    children=[
                        html.Div(
                            className='header--logo',
                            children=[
                                html.A(
                                    className='header--snap-link',
                                    children=[
                                        html.Img(src=path_prefix + 'assets/SNAP_acronym_color_square.svg')
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            className='header--titles',
                            children=[
                                html.H1(
                                    'Northwest Territories Climate Scenarios Explorer',
                                    className='title is-3'
                                ),
                                html.H2(
                                    'See temperature and precipitation projections for selected NWT locations under various climate scenarios, from now until far into the future.  Choose a location and variables to get started.',
                                    className='subtitle is-5'
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
                            src=path_prefix + 'assets/SNAP_color_all.svg'
                        )
                    ]
                ),
                html.A(
                    href='https://uaf.edu/uaf/',
                    target='_blank',
                    className='level-item',
                    children=[
                        html.Img(
                            src=path_prefix + 'assets/UAF.svg'
                        )
                    ]
                ),
                html.A(
                    href='https://www.gov.nt.ca/',
                    target='_blank',
                    className='level-item',
                    children=[
                        html.Img(
                            src=path_prefix + 'assets/NWT.svg'
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

communities_dropdown_field = html.Div(
    className='field',
    children=[
        html.Label('Location', className='label'),
        html.Div(className='control', children=[
            dcc.Dropdown(
                id='communities-dropdown',
                options=[
                    {
                        'label': i.replace('_', ' '),
                        'value': i
                    } for i in communities.index
                ],
                value='Yellowknife'
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
            values=['rcp60', 'rcp85']
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
                value=[12, 1, 2],
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
            options=list(
                map(
                    lambda k: {
                        'label': models_lut[k],
                        'value': k
                    }, models_lut
                )
            ),
            value=['NCAR-CCSM4'],
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
                communities_dropdown_field,
                dcc.Graph(
                    id='minesites-map',
                    figure=map_figure,
                    config={
                        'displayModeBar': False,
                        'scrollZoom': False
                    }
                )
            ]
        ),
        html.Div(
            className='column',
            children=[
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
            className='section section--form',
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

help_text = html.Div(
    className='container',
    children=[
        html.Div(
            className='section',
            children=[
                dcc.Markdown('''

## Climate scenarios

### Representative Concentration Pathways

RCPs describe paths to future climates based on atmospheric greenhouse gas concentrations. They represent four climate futures—scenarios—extrapolated out to the year 2100, based on a range of possible future human behaviors. RCPs provide a basis for comparison and a “common language” for modelers to share their work.

The four RCP values of 2.6, 4.5, 6.0, and 8.5 indicate projected radiative forcing values—the difference between solar energy absorbed by Earth vs. energy radiated back to space— measured in watts per square meter. RCP X projects that in 2100 the concentration of greenhouse gases will be such that each square meter of Earth will absorb X times more solar energy than it did in 1750.

* RCP 2.6—SNAP does not consider this pathway (emissions peak 2010–2020 and then decline) because it is unrealistic in light of current global emissions.
* RCP 4.5—SNAP’s “low” scenario. Assumes that emissions peak in 2040 and radiative forcing stabilizes after 2100. 
* RCP 6.0—SNAP’s “medium” scenario. Assumes that new technologies and socioeconomic strategies cause emissions to peak in 2080 and radiative forcing to stabilize after 2100.
* RCP 8.5—SNAP’s “high” scenario. Emissions increase through the 21st century.

### Extended Concentration Pathways (ECPs)

These scenarios allow extensions of RCPs for 2100–2500 by expanding the data series for greenhouse gas and land use. ECPs are intended to provide rough estimations of what climate and ocean systems might look like in a few centuries regardless of the driving forces of emissions (demography, policies, technology, and investment).


                ''', className='is-size-5 content')
            ]
        )
    ]
)

layout = html.Div(
    children=[
        header_section,
        main_layout,
        help_text,
        footer
    ]
)

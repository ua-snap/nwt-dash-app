"""
NWT Mine site future climate tool
"""
# pylint: disable=invalid-name, import-error, line-too-long, too-many-arguments
import os
import json
import base64
from collections import defaultdict
import plotly.graph_objs as go
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# #  NWT -- ANNUAL / MONTHLY DECADAL TEMPERATURE AVERAGES application   # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # APP INPUT DATA
files = [
    'tas_minesites_decadal_monthly_mean_alldata_melted.csv',
    'tas_fulldomain_decadal_monthly_mean_alldata_melted.csv',
    'pr_minesites_decadal_monthly_mean_alldata_melted.csv',
    'pr_fulldomain_decadal_monthly_mean_alldata_melted.csv'
]

files = [os.path.join('.', 'data', fn) for fn in files]

data = {'_'.join(os.path.basename(fn).split('_')[:2]):pd.read_csv(fn, index_col=0) for count, fn in enumerate(files)}

# make sure we only have the years with full decades... this is kinda tricky...
filtered_data = defaultdict( dict )
domain_lu = {'minesites':1, 'fulldomain':2}
for k, v in data.items():
    variable, domain = k.split('_')
    print(variable)
    out = []
    for i, df in v.groupby(['model', 'scenario']):
        if df['year'].max() > 2100:
            out.append(df[df['year'] <= 2290])
        else:
            out.append(df[df['year'] <= 2090])

    filtered_data[domain_lu[domain]][variable] = pd.concat(out)

del df, data

# LAYOUT STATIC IMAGES:
static_files = ['./images/funders.png']
encoded_images = [base64.b64encode(open(image_filename, 'rb').read()) for image_filename in static_files]

# welcome to the wild west folks!!! :(
data = filtered_data # ugly
df = data[1]['tas'] # hacky --> use this to build out some stuff in the layout...

pts = pd.read_csv('./data/minesites.csv', index_col=0)
nwt_shape = './data/NorthwestTerritories_4326.geojson'
mapbox_access_token = os.environ['MAPBOX_ACCESS_TOKEN']

scenarios = ['rcp45', 'rcp60', 'rcp85']

# # CONFIGURE MAPBOX AND DATA OVERLAYS
ptsd = list(pts.T.to_dict().values())
del pts # cleanup

textpositions = [
    'top center',
    'bottom center',
    'top center',
    'bottom right',
    'middle left',
    'bottom center',
    'bottom center',
    'bottom left'
]

map_traces = [
    go.Scattermapbox(
        lat=[pt['Latitude']],
        lon=[pt['Longitude']],
        mode='markers+text',
        marker=go.Marker(size=12, color='rgb(140,86,75)'),
        text=[pt['Name']],
        textposition=tp,
        hoverinfo='text'
    ) for tp, pt in zip(textpositions, ptsd)
]

mapbox_config = dict(
    accesstoken=mapbox_access_token,
    bearing=0,
    pitch=0,
    zoom=3,
    center=dict(lat=64, lon=-116.6),
    layers=[dict(
        sourcetype='geojson',
        source=json.loads(open(nwt_shape, 'r').read()),
        type='fill',
        color='rgba(163,22,19,0.1)',
        below=0
    )]
)

map_layout = go.Layout(
    autosize=True,
    hovermode='closest',
    mapbox=mapbox_config,
    showlegend=False,
    margin=dict(l=0, r=0, t=0, b=0)
)

map_figure = go.Figure(dict(data=map_traces, layout=map_layout))

# LINE COLORS LOOKUP -- hacky but somewhat working
ms_colors = {
    'GISS-E2-R': {'rcp45':'#FDD017', 'rcp60':'#F2BB66', 'rcp85':'#EAC117'},
    'GFDL-CM3': {'rcp45':'#6AA121', 'rcp60':'#347C17', 'rcp85':'#254117'},
    '5ModelAvg': {'rcp45':'#736F6E', 'rcp60':'#463E3F', 'rcp85':'#2B1B17'},
    'IPSL-CM5A-LR': {'rcp45':'#C24641', 'rcp60':'#7E3517', 'rcp85':'#800517'},
    'MRI-CGCM3': {'rcp45':'#4863A0', 'rcp60':'#2B547E', 'rcp85':'#151B54'},
    'NCAR-CCSM4': {'rcp45':'#C35817', 'rcp60':'#6F4E37', 'rcp85':'#493D26'}
}

markdown_map = '''
__How to use this application:__
- select combinations of model(s)/scenario(s)/year-ranges for a 
mine site and display plots.
- mine can also be selected from the map above.
- toggle between minesites/NWT-wide outputs with tabs. if multiple months are chosen, they are averaged.
check 'all months' for annual decadal means.
- plot is interactive and addt'l toolbars display on hover.
- __[ note ]: too many combinations of models/scenarios generates a busy graphic.__
'''

app = dash.Dash(__name__)
app.config.supress_callback_exceptions = True
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})
app.title = 'NWT Climate Scenarios Explorer' # this is a hack and will break in the future...

# # BUILD PAGE LAYOUT
app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    [
                                        html.Div(
                                            [
                                                html.Span('Northwest Territories ', style={'color':'#4399AE', 'font-family':'Calibri'}),
                                                html.Span('Climate Scenarios Explorer', style={'color':'#96A73A', 'font-family':'Calibri'}),
                                                html.Span('.', style={'color':'rgba(230, 249, 255,0.3)'})
                                            ],
                                            style={
                                                'border-style':'solid',
                                                'border-width':2,
                                                'background-color':'rgba(242, 242, 242,0.25)',#'rgba(230, 249, 255,0.3)',
                                                'border-color':'rgb(67, 153, 174)',
                                                'border-radius':'5',
                                                'box-sizing': 'content-box',
                                                'float': 'left'
                                            }
                                        )
                                    ]
                                )
                            ],
                            className='nine columns'
                        ),
                        html.Div(
                            [
                                html.Img(
                                    src='data:image/png;base64,{}'.format(encoded_images[0].decode()),
                                    style={'width': '200px'}
                                )
                            ],
                            className='three columns'
                        )
                    ],
                    id='mdown-head',
                    className='row'
                )
            ]
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Tabs(
                            id='tabs',
                            children=[
                                dcc.Tab(label='Mine Sites', value=1),
                                dcc.Tab(label='NWT Province-wide', value=2)
                            ],
                            value=1,
                            vertical=False
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label(
                                            'Choose Minesite',
                                            style={'font-weight':'bold'}
                                        ),
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
                                        )
                                    ],
                                    id='mines-div',
                                    className='four columns'
                                ),
                                html.Div(
                                    [
                                        html.Label(
                                            'Choose Scenario(s)',
                                            style={'font-weight':'bold'}
                                        ),
                                        dcc.Checklist(
                                            id='scenario-check',
                                            options=[
                                                {
                                                    'label': i,
                                                    'value': i
                                                } for i in scenarios
                                            ],
                                            values=['rcp85'],
                                            labelStyle={'display': 'inline-block'}
                                        )
                                    ],
                                    className='four columns'
                                ),
                                html.Div(
                                    [
                                        html.Label(
                                            'Choose Variable',
                                            style={'font-weight':'bold'}
                                        ),
                                        dcc.Dropdown(
                                            id='variable-dropdown',
                                            options=[
                                                {
                                                    'label': i,
                                                    'value': i
                                                } for i in ['tas', 'pr']
                                            ],
                                            value='tas',
                                            multi=False,
                                            disabled=False
                                        )
                                    ],
                                    className='four columns'
                                ),
                                html.Div(
                                    [
                                        html.Label(
                                            'Choose Month(s)',
                                            style={'font-weight':'bold'}
                                        ),
                                        dcc.Checklist(
                                            id='all-month-check',
                                            options=[{'label':'all months', 'value':'all'}],
                                            values=[],
                                            labelStyle={'display': 'inline-block'}
                                        ),
                                        dcc.Dropdown(
                                            id='month-dropdown',
                                            options=[{'label': i, 'value': i} for i in list(range(1, 12+1))],
                                            value=[1],
                                            multi=True,
                                            disabled=False
                                        )
                                    ],
                                    id='month-div',
                                    className='four columns'
                                )
                            ],
                            className='row'
                        ),
                        html.Label('Choose Model(s)', style={'font-weight':'bold'}),
                        dcc.Dropdown(
                            id='model-dropdown',
                            options=[{'label': i, 'value': i} for i in df.model.unique()],
                            value=['IPSL-CM5A-LR'],
                            multi=True
                        ),
                        dcc.Graph(id='my-graph'),
                        html.Div(
                            [
                                dcc.RangeSlider(
                                    id='range-slider',
                                    marks={str(year): str(year) for year in df['year'].unique()[::2]},
                                    min=df['year'].min(),
                                    max=df['year'].max(),
                                    step=1,
                                    value=[df['year'].unique().min(), df['year'].unique().max()],
                                )
                            ], style={'width':'85%', 'margin':'0 auto'}
                        ),
                    ],
                    className="eight columns"
                ),
                html.Div(
                    [
                        dcc.Graph(id='minesites-map', figure=map_figure),
                        dcc.Markdown(children=markdown_map)
                    ],
                    className="four columns"
                ),
            ]
        ),
        html.Div(
            id='intermediate-value',
            style={'display': 'none'}
        ),
    ]
)

# cleanup
del df 
df = None

# INTERACTIVITY
@app.callback(
    Output('mines-div', 'style'),
    [Input('tabs', 'value')]
)
def update_mines_div(selected_tab_value):
    if selected_tab_value == 1:
        return None
    elif selected_tab_value == 2:
        return {'display': 'none'}


@app.callback(
    Output('minesites-dropdown', 'value'),
    [Input('minesites-map', 'clickData')]
)
def update_minesite_radio(clickdata):
    if clickdata is not None: # make it draw the inital graph before a clickevent
        return clickdata['points'][0]['text'].replace(' ', '_')
    else:
        return 'Prairie_Creek_Mine'

def average_months(dff, model, scenario, variable_value):
    '''
    in case of multiple months allowed to be chosen
    average all of the months together to single traces.
    '''
    print('averaging months')
    sub_df = dff[(dff['model'] == model) & (dff['scenario'] == scenario)]
    dfm = sub_df.groupby('month').apply(lambda x: x[variable_value].reset_index(drop=True)).T.mean(axis=1).copy()
    # convert back to a DataFrame from the output Series...
    dfm = dfm.to_frame(name=variable_value).reset_index(drop=True)
    dfm['year'] = sub_df['year'].unique()
    dfm['model'] = model
    dfm['scenario'] = scenario
    dfm['month'] = '_'.join(['avg'] + [str(m) for m in dff.month.unique()])
    return dfm

@app.callback(
    Output('intermediate-value', 'children'),
    [
        Input('tabs', 'value'),
        Input('minesites-dropdown', 'value'),
        Input('range-slider', 'value'),
        Input('scenario-check', 'values'),
        Input('model-dropdown', 'value'),
        Input('month-dropdown', 'value'),
        Input('all-month-check', 'values'),
        Input('variable-dropdown', 'value')
    ]
)
def prep_data(selected_tab_value, minesite, year_range, scenario_values, model_values, months, all_check, variable_value):
    """ Prepare data per user input """
    import itertools
    print('prepping data')
    print(f'selected_tab_value: {selected_tab_value}')
    print(f'variable:{variable_value}')

    cur_df = data[selected_tab_value][variable_value].copy()
    if 'group' in cur_df.columns:
        cur_df = cur_df.drop('group', axis=1)

    if selected_tab_value == 1:
        dff = cur_df[(cur_df.minesite == minesite)].copy()
    else:
        dff = cur_df.copy()

    begin_range, end_range = year_range
    dff = dff[(dff['year'] >= begin_range) & (dff['year'] <= end_range)]
    dff = dff.loc[dff['scenario'].isin(scenario_values),]
    dff = dff.loc[dff['model'].isin(model_values),]

    # months
    if 'all' in all_check:
        months = list(range(1, 12+1))

    dff = dff.loc[dff['month'].isin(months),]

    if len(dff.month.unique()) > 1:
        dff = pd.concat([average_months(dff, m, s, variable_value) for m, s in itertools.product(dff.model.unique(), dff.scenario.unique())], axis=0)

    dff = dff.reset_index(drop=True)
    return dff.to_json()

@app.callback(
    Output('my-graph', 'figure'),
    [
        Input('intermediate-value', 'children'),
        Input('all-month-check', 'values'),
        Input('variable-dropdown', 'value')
    ]
)
def update_graph(data, all_check, variable_value):
    """ Update graph from current application state """
    print('updating graph')
    print(data)
    dff = pd.read_json(data).sort_index()
    print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
    print(dff.columns)

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
        'data':[
            go.Scatter(
                x=j['year'],
                y=j[variable_value],
                name=i[0] + ' ' + i[1],
                line=dict(color=ms_colors[i[0]][i[1]], width=2),
                mode='lines'
            ) for i, j in dff.groupby(['model', 'scenario', 'month'])
        ],
        'layout':{
            'title': title,
            'xaxis': dict(title='Decades'),
            'yaxis': dict(title=yaxis_title[variable_value])
        }
    }

@app.callback(
    Output('month-dropdown', 'disabled'),
    [Input('all-month-check', 'values')]
)
def disable_month_dropdown( month_check):
    """ Disable the month dropdown if "All" is checked """
    if 'all' in month_check:
        return True
    else:
        return False

if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server()

# # # # TEMP: FOR TESTING
# selected_tab_value = 2
# minesite = 'Prairie_Creek_Mine'
# year_range = (2000, 2090)
# scenario_values = ['rcp45', 'rcp85']
# model_values = ['IPSL-CM5A-LR', 'MRI-CGCM3']
# months = [1,2]

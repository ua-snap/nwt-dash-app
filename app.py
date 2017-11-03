import dash, os, glob, json
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import geopandas as gpd
import numpy as np
import base64

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# #  NWT -- ANNUAL / MONTHLY DECADAL TEMPERATURE AVERAGES application   # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # APP INPUT DATA
files = [ 'tas_minesites_decadal_monthly_mean_alldata_melted.csv', 
            'tas_fulldomain_decadal_monthly_mean_alldata_melted.csv' ]

files = [ os.path.join( '.','data',fn ) for fn in files ]
data = { count+1:pd.read_csv(fn, index_col=0) for count, fn in enumerate( files ) }
# make sure we only have the years with full decades... this is kinda tricky...
filtered_data = dict()
for k,v in data.items():
    out = []
    for i,df in v.groupby(['model','scenario']):
        if df['year'].max() > 2100:
            out.append( df[df['year'] <= 2290 ] )
        else:
            out.append( df[df['year'] <= 2090 ] )
        filtered_data[k] = pd.concat( out )

del df, data

# LAYOUT STATIC IMAGES:
static_files = ['./images/funders.png']
encoded_images = [base64.b64encode(open(image_filename, 'rb').read()) for image_filename in static_files]

# welcome to the wild west folks!!! :(
data = filtered_data # ugly
df = data[1] # hacky --> use this to build out some stuff in the layout...

pts = pd.read_csv( './data/minesites.csv', index_col=0 )
nwt_shape = './data/NorthwestTerritories_4326.geojson'
mapbox_access_token = os.environ.get('MAPBOX_ACCESS_TOKEN')
scenarios = ['rcp45','rcp60','rcp85']

# # CONFIGURE MAPBOX AND DATA OVERLAYS
ptsd = list(pts.T.to_dict().values())
del pts # cleanup
# MINE_ORDER_REFERENCE = ['CanTung Mine', 'Diavik Mine', 'Ekati Mine', 'Gahcho Kue Mine', 
#                            'NICO Mine', 'Pine Point Mine (Tamerlane)', 'Prairie Creek Mine', 'Snap Lake Mine'] 

textpositions = ['top center','bottom center','top center','bottom right','middle left',
                    'below center','below center','bottom left']
map_traces = [ go.Scattermapbox(
            lat=[pt['Latitude']],
            lon=[pt['Longitude']],
            mode='markers+text',
            marker=go.Marker(size=12, color='rgb(140,86,75)'),
            text=[pt['Name']],
            textposition=tp,
            hoverinfo='text' ) for tp,pt in zip(textpositions, ptsd) ]

mapbox_config = dict(accesstoken=mapbox_access_token,
                        bearing=0,
                        pitch=0,
                        zoom=3,
                        center=dict(lat=64,
                                    lon=-116.6),
                        layers=[ dict( sourcetype='geojson',
                                        source=json.loads(open(nwt_shape,'r').read()),
                                        type='fill',
                                        color='rgba(163,22,19,0.1)',
                                        below=0 )]
                        )

map_layout = go.Layout(
                    autosize=True,
                    hovermode='closest',
                    mapbox=mapbox_config,
                    showlegend=False,
                    margin = dict(l = 0, r = 0, t = 0, b = 0)
                     )

map_figure = go.Figure( dict(data=map_traces, layout=map_layout) )

# LINE COLORS LOOKUP -- hacky but somewhat working
ms_colors = {'GISS-E2-R':{'rcp45':'#FDD017','rcp60':'#F2BB66','rcp85':'#EAC117'},
            'GFDL-CM3':{'rcp45':'#6AA121','rcp60':'#347C17','rcp85':'#254117'},
            '5ModelAvg':{'rcp45':'#736F6E','rcp60':'#463E3F','rcp85':'#2B1B17'},
            'IPSL-CM5A-LR':{'rcp45':'#C24641','rcp60':'#7E3517','rcp85':'#800517'},
            'MRI-CGCM3':{'rcp45':'#4863A0','rcp60':'#2B547E','rcp85':'#151B54'},
            'NCAR-CCSM4':{'rcp45':'#C35817','rcp60':'#6F4E37','rcp85':'#493D26'} }


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
server = app.server
server.secret_key = os.environ.get('SERVER_SECRET_KEY')
app.config.supress_callback_exceptions = True
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

# # BUILD PAGE LAYOUT
app.layout = html.Div([ 
                html.Div([
                    html.Div([
                            html.Div([
                                html.H4('NWT Climate Scenarios Explorer'),
                                dcc.Markdown(children='Decadal Monthly Mean Temperatures')],
                            className='nine columns'),
                            html.Div([ html.Img(src='data:image/png;base64,{}'.format(encoded_images[0].decode()), style={'width': '250px'}) ], className='three columns' ),
                            # html.Div([ html.Img(src='data:image/gif;base64,{}'.format(encoded_images[0].decode())) ], className='')
                        ], id='mdown-head', className='row'),

                        ]),
                html.Div([ 
                    html.Div([
                        dcc.Tabs( 
                            id='tabs',
                            tabs=[
                                {'label': 'Mine Sites', 'value': 1},
                                {'label': 'NWT Province-wide', 'value': 2},
                            ],
                            value=1,
                            vertical=False
                        ),
                        html.Div([
                            html.Div([ html.Label('Choose Minesite', style={'font-weight':'bold'}),
                                     dcc.Dropdown( id='minesites-dropdown',
                                        options=[ {'label':i.replace('_', ' '), 'value':i} for i in df.minesite.unique() ],
                                        value='Prairie_Creek_Mine',
                                        multi=False,
                                        )], id='mines-div', className='four columns' ),

                            html.Div([ html.Label('Choose Scenario(s)', style={'font-weight':'bold'}),
                                    dcc.Checklist( id='scenario-check',
                                        options=[{'label': i, 'value': i} for i in scenarios ], #df.scenario.unique()
                                        values=['rcp85'],
                                        labelStyle={'display': 'inline-block'}
                                    )], className='four columns'),
                            html.Div([ 
                                        html.Label('Choose Month(s)', style={'font-weight':'bold'}),
                                        dcc.Checklist(id='all-month-check', 
                                            options=[{'label':'all months','value':'all'}],
                                            values=[],
                                            labelStyle={'display': 'inline-block'} ),
                                        dcc.Dropdown(
                                            id='month-dropdown',
                                            options=[ {'label':i, 'value':i} for i in list(range(1, 12+1)) ],
                                            value=[1],
                                            multi=True,
                                            disabled=False ) ], id='month-div', className='four columns')
                            ], className='row'),

                        html.Label('Choose Model(s)', style={'font-weight':'bold'}),
                        dcc.Dropdown(
                            id='model-dropdown',
                            options=[ {'label':i, 'value':i} for i in df.model.unique() ],
                            value=['IPSL-CM5A-LR'],
                            multi=True
                        ),
                        dcc.Graph( id='my-graph' ),
                        html.Div([
                            dcc.RangeSlider( id='range-slider',
                                marks={str(year): str(year) for year in df['year'].unique()[::2]},
                                min=df['year'].min(),
                                max=df['year'].max(),
                                step=1,
                                value=[df['year'].unique().min(), df['year'].unique().max()]
                            )
                        ], className='eleven columns'),
                    ], className="eight columns" ),

                    html.Div([
                        dcc.Graph( id='minesites-map', figure=map_figure ),
                        dcc.Markdown( children=markdown_map )
                    ], className="four columns" ),
            ]),
        html.Div(id='intermediate-value', style={'display': 'none'}),
        ])

# cleanup
del df 
df = None

# # INTERACTIVITY 
@app.callback( Output('mines-div', 'style'), [Input('tabs','value')] )
def update_mines_div( selected_tab_value ):
    # print('selected_tab_value={}'.format(selected_tab_value) )
    if selected_tab_value == 1:
        return None
    elif selected_tab_value == 2:
        return {'display': 'none'}


@app.callback( Output('minesites-dropdown', 'value'), [Input('minesites-map', 'clickData')])
def update_minesite_radio( clickdata ):
    # print(clickdata)
    if clickdata is not None: # make it draw the inital graph before a clickevent
        return clickdata['points'][0]['text'].replace(' ', '_')
    else:
        return 'Prairie_Creek_Mine'

def average_months( dff, model, scenario ):
    ''' 
    in case of multiple months allowed to be chosen
    average all of the months together to single traces.
    '''
    print('averaging months')
    sub_df = dff[(dff['model'] == model) & (dff['scenario'] == scenario)]
    dfm = sub_df.groupby( 'month' ).apply(lambda x: x['tas'].reset_index(drop=True)).T.mean(axis=1).copy()
    # convert back to a DataFrame from the output Series...
    dfm = dfm.to_frame(name='tas').reset_index(drop=True)
    dfm['year'] = sub_df['year'].unique()
    dfm['model'] = model
    dfm['scenario'] = scenario
    dfm['month'] = '_'.join(['avg'] + [ str(m) for m in dff.month.unique() ])
    return dfm

@app.callback( Output('intermediate-value', 'children'), 
                [Input('tabs', 'value'),
                Input('minesites-dropdown', 'value'),
                Input('range-slider', 'value'),
                Input('scenario-check', 'values'),
                Input('model-dropdown', 'value'),
                Input('month-dropdown','value'),
                Input('all-month-check', 'values')] )
def prep_data( selected_tab_value, minesite, year_range, scenario_values, model_values, months, all_check ):
    import itertools
    print( 'prepping data' )

    cur_df = data[ selected_tab_value ].copy()
    if 'group' in cur_df.columns:
        cur_df = cur_df.drop( 'group', axis=1 )
   
    if selected_tab_value == 1:
        dff = cur_df[ (cur_df.minesite == minesite) ].copy()
    else:
        dff = cur_df.copy()

    begin_range, end_range = year_range
    dff = dff[ (dff['year'] >= begin_range) & (dff['year'] <= end_range) ]
    dff = dff.loc[ dff[ 'scenario' ].isin( scenario_values ), ]
    dff = dff.loc[ dff[ 'model' ].isin( model_values ), ]
    
    # months
    if 'all' in all_check:
        months = list(range(1,12+1))

    dff = dff.loc[ dff[ 'month' ].isin( months ), ]

    if len(dff.month.unique()) > 1:
        dff = pd.concat([ average_months( dff, m, s ) for m,s in itertools.product(dff.model.unique(), dff.scenario.unique()) ], axis=0)

    dff = dff.reset_index(drop=True)
    return dff.to_json()

@app.callback( Output('my-graph', 'figure'), [Input('intermediate-value', 'children')] )
def update_graph( data ):
    print('updating graph')
    dff = pd.read_json( data ).sort_index()

    if 'month' in dff.columns:
        # its monthlies
        return {'data':[ go.Scatter( x=j['year'], 
                        y=j['tas'], 
                        name=i[0]+' '+i[1], 
                        line=dict(color=ms_colors[i[0]][i[1]], width=2 ),
                        mode='lines') for i,j in dff.groupby(['model','scenario','month']) ] }
    else:
        # its annuals
        return {'data':[ go.Scatter( x=j['year'], 
                                y=j['tas'],
                                name=i[0]+' '+i[1], 
                                line=dict(color=ms_colors[i[0]][i[1]], width=2 ),
                                mode='lines') for i,j in dff.groupby(['model','scenario']) ] }

@app.callback( Output('month-dropdown', 'disabled'), [Input('all-month-check','values')] )
def disable_month_dropdown( month_check ):
    if 'all' in month_check:
        return True
    else:
        return False

# @app.callback( Output('month-dropdown', 'value'), [Input('all-month-check','values')] )
# def update_month_dropdown_disabled( month_check ):
#     if 'all' in month_check:
#         return True
#     else:
#         return False


if __name__ == '__main__':
    app.run_server( debug=True )


# # # # TEMP: FOR TESTING
# selected_tab_value = 2
# minesite = 'Prairie_Creek_Mine'
# year_range = (2000, 2090)
# scenario_values = ['rcp45', 'rcp85']
# model_values = ['IPSL-CM5A-LR', 'MRI-CGCM3']
# months = [1,2]

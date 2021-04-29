"""
NWT Mine site future climate tool
"""
# pylint: disable=invalid-name, import-error, line-too-long, too-many-arguments
import os
import json
import itertools
import plotly.graph_objs as go
import dash
from dash.dependencies import Input, Output
import pandas as pd
from gui import layout, map_layout, map_communities_trace, months_lut, variables_lut, models_lut, scenarios_lut, ms_colors

# Read pickled data blobs and other items used from env
data = pd.read_pickle('data.pickle')
communities = pd.read_pickle('community_places.pickle')
mapbox_access_token = os.environ['MAPBOX_ACCESS_TOKEN']

app = dash.Dash(__name__)

# AWS Elastic Beanstalk looks for application by default,
# if this variable (application) isn't set you will get a WSGI error.
application = app.server

# The next config sets a relative base path so we can deploy
# with custom URLs.
# https://community.plot.ly/t/dash-error-loading-layout/8139/6
app.config.requests_pathname_prefix = os.environ['REQUESTS_PATHNAME_PREFIX']

# Customize this layout to include Google Analytics
gtag_id = os.environ['GTAG_ID']
app.index_string = f'''
<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-3978613-12"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());

          gtag('config', '{gtag_id}');
        </script>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
'''

app.title = 'NWT Climate Scenarios Explorer'
app.layout = layout

def build_plot_title(location, variable, start, end, annual, months, scenarios, models):
    ''' Return a string containing the map title '''
    def join_strings_with_commas(lut, items):
        return ', '.join(list(map(lambda k: lut[k], items))).rstrip(', ')

    title = location + '<br>'
    if annual:
        title += 'Decadal Annual Mean '
        months_fragment = ''
    else:
        title += 'Decadal Monthly Mean '
        months.sort()
        months_fragment = '<br>' + join_strings_with_commas(months_lut, months)
        if len(months) > 1:
            months_fragment += ' Averaged'

    title += variables_lut[variable] + ', ' + str(start) + '-' + str(end) + months_fragment

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

    # Round to one digit
    dfm[variable_value] = dfm[variable_value].apply(
        lambda x: round(x, 1)
    )

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
    Output('communities-dropdown', 'value'),
    [
        Input('minesites-map', 'clickData')
    ]
)
def update_mine_site_dropdown(selected_on_map):
    """ If user clicks on the map, update the drop down. """

    # if "territory-wide" is checked, ignore map clicks
    if selected_on_map is not None:
        return selected_on_map['points'][0]['text']
    # Return a default
    return 'Aklavik'

@app.callback(
    Output('minesites-map', 'figure'),
    [
        Input('communities-dropdown', 'value')
    ]
)
def update_selected_community_on_map(community):
    """ Draw a second trace on the map with one community highlighted. """
    return {
        'data': [
            map_communities_trace,
            go.Scattermapbox(
                lat=[communities.loc[community]['latitude']],
                lon=[communities.loc[community]['longitude']],
                mode='markers',
                marker={
                    'size': 20,
                    'color': 'rgb(207, 38, 47)'
                },
                line={
                    'color': 'rgb(0, 0, 0)',
                    'width': 2
                },
                text=community,
                hoverinfo='text'
            )
        ],
        'layout': map_layout
    }

@app.callback(
    Output('my-graph', 'figure'),
    [
        Input('communities-dropdown', 'value'),
        Input('range-slider', 'value'),
        Input('scenario-check', 'values'),
        Input('model-dropdown', 'value'),
        Input('month-dropdown', 'value'),
        Input('all-month-check', 'values'),
        Input('variable-toggle', 'value')
    ]
)
def update_graph(
        community,
        year_range,
        scenario_values,
        model_values,
        months,
        all_check,
        variable_value
    ):
    """ Update graph from UI controls """

    from pprint import pprint
    pprint(all_check)

    # TBD: Handle case when no community is selected,
    # Or other variables are missing such that the
    # graph is blank??
    if not community or not scenario_values or not model_values or (not months and not all_check):
        return None

    # Subset community, scenarios, and models
    selected = data[data.community.isin([community])]
    selected = selected[selected.scenario.isin(scenario_values)]
    selected = selected[selected.model.isin(model_values)]

    # Subset by year range
    begin_range, end_range = year_range
    selected = selected[(selected['year'] >= begin_range) & (selected['year'] <= end_range)]


    # Filter by months
    if 'all' in all_check:
        months = list(range(1, 13))

    selected = selected.loc[selected['month'].isin(months), ]

    # Perform averages grouped by model/scenario over selected months
    if len(selected.month.unique()) > 1:
        selected = pd.concat([average_months(selected, model, scenario, variable_value) for model, scenario in itertools.product(
            selected.model.unique(), selected.scenario.unique())], axis=0)

    selected = selected.reset_index(drop=True)

    title = build_plot_title(community, variable_value, begin_range, end_range, all_check, months, scenario_values, model_values)

    yaxis_title = {
        'tas': 'Degrees Celsius',
        'pr': 'Millimeters'
    }

    return {
        'data': [
            go.Scatter(
                x=j['year'],
                y=j[variable_value],
                name=models_lut[i[0]] + ' ' + scenarios_lut[i[1]],
                line=dict(color=ms_colors[i[0]][i[1]], width=2),
                mode='lines'
            ) for i, j in selected.groupby(['model', 'scenario', 'month'])
        ],
        'layout': {
            'title': title,
            'autosize': False,
            'showlegend': True,
            'height': 650,
            'margin': dict(t=100, b=130),
            'xaxis': dict(title='Year'),
            'yaxis': dict(title=yaxis_title[variable_value]),
            'annotations': [
                {
                    'x': 0.5,
                    'y': -0.20,
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'text': 'These plots are useful for examining possible trends over time, rather than for precisely predicting values.'
                },
                {
                    'x': 0.5,
                    'y': -0.24,
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'text': 'Credit: Scenarios Network for Alaska + Arctic Planning, University of Alaska Fairbanks.'
                }],
        }
    }


if __name__ == '__main__':
    application.run(debug=True, port=8080)

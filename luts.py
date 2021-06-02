import os
import json
import plotly.graph_objs as go
import pandas as pd


# The next config sets a relative base path so we can deploy
# with custom URLs.
if os.environ.get("REQUESTS_PATHNAME_PREFIX"):
    path_prefix = os.getenv("REQUESTS_PATHNAME_PREFIX")
else:
    path_prefix = "/"

# Google analytics tag
gtag_id = "UA-3978613-12"

# Lookup tables for a few things used in form inputs & graph title
variables_lut = {"tas": "Temperature", "pr": "Precipitation"}

# Spaces after are to address a padding issue in the legend
# for PNG download
scenarios_lut = {
    "rcp45": "4.5 Scenario",
    "rcp60": "6.0 Scenario",
    "rcp85": "8.5 Scenario",
}

months_lut = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}

models_lut = {
    "GISS-E2-R": "GISS-E2-R",
    "GFDL-CM3": "GFDL-CM3",
    "5ModelAvg": "Five Model Average",
    "IPSL-CM5A-LR": "IPSL-CM5A-LR",
    "MRI-CGCM3": "MRI-CGCM3",
    "NCAR-CCSM4": "NCAR-CCSM4",
}


# LINE COLORS LOOKUP -- hacky but somewhat working
ms_colors = {
    "GISS-E2-R": {"rcp45": "#FDD017", "rcp60": "#F2BB66", "rcp85": "#EAC117"},
    "GFDL-CM3": {"rcp45": "#6AA121", "rcp60": "#347C17", "rcp85": "#254117"},
    "5ModelAvg": {"rcp45": "#736F6E", "rcp60": "#463E3F", "rcp85": "#2B1B17"},
    "IPSL-CM5A-LR": {"rcp45": "#C24641", "rcp60": "#7E3517", "rcp85": "#800517"},
    "MRI-CGCM3": {"rcp45": "#4863A0", "rcp60": "#2B547E", "rcp85": "#151B54"},
    "NCAR-CCSM4": {"rcp45": "#C35817", "rcp60": "#6F4E37", "rcp85": "#493D26"},
}

communities = pd.read_pickle("community_places.pickle")
communities = communities.reset_index()
communities = communities.rename(columns={"index": "name"})

mapbox_access_token = os.environ["MAPBOX_ACCESS_TOKEN"]

# This trace is shared so we can highlight specific communities.
places_trace = go.Scattermapbox(
    lat=communities.loc[:, "latitude"],
    lon=communities.loc[:, "longitude"],
    mode="markers",
    marker={"size": 10, "color": "rgb(80,80,80)"},
    line={"color": "rgb(0, 0, 0)", "width": 2},
    text=communities.loc[:, "name"],
    hoverinfo="text",
)

map_layout = go.Layout(
    autosize=True,
    hovermode="closest",
    mapbox=dict(style="carto-positron", zoom=3.25, center=dict(lat=66.75, lon=-125)),
    showlegend=False,
    margin=dict(l=0, r=0, t=0, b=0),
)

"""
Tiny script to prepare placenames with lat/lon.
"""

# pylint: disable=invalid-name, import-error, line-too-long, too-many-arguments

import pandas as pd

df = pd.read_csv('nwt_point_locations.csv')
df.index = df['name']
df[['latitude','longitude']].to_pickle('../tcommunity_places.pickle')


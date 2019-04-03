"""
Tiny script to prepare placenames with lat/lon.
Data source is large so not included in source control.
"""

# pylint: disable=invalid-name, import-error, line-too-long, too-many-arguments

import pandas as pd

communities_fn = '../data/SNAP_comm_charts_export_20160926_fix_021119.csv'
minesites_fn = '../data/minesites.csv'

# prepare the points for use in extraction of profiles
communities = pd.read_csv(communities_fn)
communities = communities[communities.region == 'Northwest Territories']
minesites = pd.read_csv(minesites_fn)

# get the unique points values to use in extractions
lonlats = communities.groupby('community').first()[['latitude', 'longitude']]
lonlats_mines = minesites[['Latitude', 'Longitude']]
lonlats_mines.index = minesites['Name']
lonlats_mines.columns = ['latitude', 'longitude']

# Last three do not deduplicate for whatever reason.
lonlats = pd.concat([lonlats, lonlats_mines]).drop_duplicates()[:-3]

lonlats.to_pickle('community_places.pickle')

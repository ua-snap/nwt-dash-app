"""
Take melted data and produce a binary pickle to be use by the Dash app.
"""
# pylint: disable=invalid-name, import-error

import os
from collections import defaultdict
import pickle
import pandas as pd

files = [
    'data/tas_pr_nwt_decadal_mean_historical_melted.csv',
    'data/tas_pr_nwt_decadal_mean_rcp45_melted.csv',
    'data/tas_pr_nwt_decadal_mean_rcp60_melted.csv',
    'data/tas_pr_nwt_decadal_mean_rcp85_melted.csv',
]

# Create dictionary of data frames, in the format
# rcp45: [dataframe from csv]
data = {
    '_'.join(os.path.basename(file).split('_')[5:6]):
        pd.read_csv(
            file,
            index_col=0
        )
    for file in files
}

output_data = pd.concat(
    [
        data['historical'],
        data['rcp45'],
        data['rcp60'],
        data['rcp85']
    ],
    ignore_index=True
)

output_data.to_pickle('data.pickle')

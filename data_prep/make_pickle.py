"""
Take melted data and produce a binary pickle to be use by the Dash app.
"""
import os
from collections import defaultdict
import pickle
import pandas as pd

# # APP INPUT DATA
files = [
    'tas_minesites_decadal_monthly_mean_alldata_melted.csv',
    'tas_fulldomain_decadal_monthly_mean_alldata_melted.csv',
    'pr_minesites_decadal_monthly_mean_alldata_melted.csv',
    'pr_fulldomain_decadal_monthly_mean_alldata_melted.csv'
]

files = [os.path.join('.', 'data', fn) for fn in files]

data = {
    '_'.join(
        os.path.basename(fn).split('_')[
            :2]): pd.read_csv(
                fn,
                index_col=0) for count,
    fn in enumerate(files)}

# make sure we only have the years with full decades... this is kinda tricky...
filtered_data = defaultdict(dict)
domain_lu = {'minesites': 1, 'fulldomain': 2}
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

# welcome to the wild west folks!!! :(
data = filtered_data  # ugly

with open('data.pickle', 'wb') as handle:
    pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
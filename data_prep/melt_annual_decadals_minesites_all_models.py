# preprocess the minesites data for use in the dash-app

def split_fn( fn ):
    dirname, basename = os.path.split( fn )
    d = dict(zip(['var','metric','model','scenario','timestep','agg'], 
                basename.split( '_' )[:6]))
    d.update( fn=fn ) # slice off junk at end
    return d

def melt_it( fn ):
    attrs = split_fn( fn )
    df = pd.read_csv( fn, index_col=0 )
    df = df.reset_index()
    cols = list( df.columns )
    cols[0] = 'year'
    df.columns = cols
    df = df.melt( id_vars=['year'], value_vars=[i for i in df.columns if i is not 'year' ])
    cols = ['year','minesite','tas']
    df.columns = cols
    df['year'] = [ int(i.split('s')[0]) for i in df.year ]
    df['group'] = '{}_{}'.format(attrs['timestep'],attrs['agg'])
    df['model'] = attrs['model']
    df['scenario'] = attrs['scenario']
    return df

if __name__ == '__main__':
    import os, glob
    import pandas as pd
    import numpy as np
    
    csv_path = '/workspace/Shared/Tech_Projects/DeltaDownscaling/project_data/NWT_DELIVERABLES/derived/tabular/mine_sites_profiles/annual_decadals_from_monthly_decadals'
    output_path = '/workspace/Shared/Tech_Projects/DeltaDownscaling/project_data/NWT_DELIVERABLES/downscaled/tabular/downscaled_domain_means/app_data'
    l = [ i for i in glob.glob( os.path.join( csv_path, 'tas_*.csv') ) if '_historical_' not in i ]
    df = pd.concat([ melt_it( fn ) for fn in l ])

    df.to_csv(os.path.join(output_path, 'tas_minesites_decadal_annual_mean_alldata_melted.csv'))
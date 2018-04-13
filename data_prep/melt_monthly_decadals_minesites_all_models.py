# preprocess the minesites monthlies data for use in the dash-app

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
    df['month'] = [ i.split('_')[-2] for i in df['index'] ]
    df['year'] = [ i.split('_')[-1].strip('s') for i in df['index'] ]
    df['scenario'] = [ i.split('_')[-3] for i in df['index'] ]
    df['model'] = [ i.split('_')[-4] for i in df['index'] ]
    df = df.drop( 'index', axis=1 )
    # cols[0] = 'year'
    # df.columns = cols
    df = df.melt( id_vars=['year', 'month', 'scenario', 'model'])
    cols = ['year','month','scenario','model','minesite','tas']
    df.columns = cols
    # df['group'] = '{}_{}'.format(attrs['timestep'],attrs['agg'])
    return df

if __name__ == '__main__':
    import os, glob
    import pandas as pd
    import numpy as np
    
    csv_path = '/workspace/Shared/Tech_Projects/DeltaDownscaling/project_data/project_data_delivery/NWT_DELIVERABLES/derived/tabular/mine_sites_profiles/monthly_decadals'
    output_path = '/workspace/Shared/Tech_Projects/DeltaDownscaling/project_data/project_data_delivery/NWT_DELIVERABLES/downscaled/tabular/downscaled_domain_means/app_data'
    # output_path = '/workspace/Shared/Tech_Projects/DeltaDownscaling/project_data/test'
    variable = 'pr'
    l = [ i for i in glob.glob( os.path.join( csv_path, '{}_*.csv'.format(variable)) ) if '_historical_' not in i ]
    df = pd.concat([ melt_it( fn ) for fn in l ])

    df.to_csv( os.path.join( output_path, '{}_minesites_decadal_monthly_mean_alldata_melted.csv'.format(variable) ) )
# melt data for input to the tool as a giant csv queryable by PANDAS
def make_monthly_decadals( fn ):
    ''' acrobatics to melt the NWT-wide data for app use'''
    df = pd.read_csv( fn, index_col=0 )
    decades = df.year.astype( str ).apply( lambda x: int(x[:3]+'0') )
    mondec = [ '{}-{}'.format(*i) for i in zip( decades, df.month )]
    decadal_monthly_mean = df.groupby( mondec ).apply( np.mean )
    monyear = [ i.split('-') for i in decadal_monthly_mean.index]
    months = [ i[1] for i in monyear ]
    months = [ str(i) if len(str(i)) == 2 else ('0'+str(i)) for i in months ]
    years = [ i[0] for i in monyear ]
    decadal_monthly_mean['month'] = months
    decadal_monthly_mean['year'] = years
    decadal_monthly_mean = decadal_monthly_mean.sort_values(['year','month'])
    decadal_monthly_mean = decadal_monthly_mean.melt(id_vars=['year','month'])
    model_scenario = [ i.split('_') for i in  decadal_monthly_mean['variable'].tolist()]
    decadal_monthly_mean['model'] = [ i[0] for i in model_scenario ]
    decadal_monthly_mean['scenario'] = [ i[1] for i in model_scenario ]
    decadal_monthly_mean = decadal_monthly_mean.drop('variable', axis=1)
    decadal_monthly_mean.columns = [ 'tas' if i == 'value' else i for i in decadal_monthly_mean.columns ]
    return decadal_monthly_mean

if __name__ == '__main__':
    import os, glob
    import pandas as pd
    import numpy as np

    # monthly decadals
    csv_path = '/workspace/Shared/Tech_Projects/DeltaDownscaling/project_data/NWT_DELIVERABLES/downscaled/tabular/downscaled_domain_means'
    output_path = '/workspace/Shared/Tech_Projects/DeltaDownscaling/project_data/NWT_DELIVERABLES/downscaled/tabular/downscaled_domain_means/app_data'
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    l = [ i for i in glob.glob( os.path.join( csv_path, 'tas_*.csv' )) if '_historical_' not in i ]
    df = pd.concat([ make_monthly_decadals( fn ) for fn in l ])

    df.to_csv(os.path.join(output_path, 'tas_fulldomain_decadal_monthly_mean_alldata_melted.csv'))

    # annual decadals
    df2 = df.groupby(['year', 'model','scenario'])\
            .apply(np.mean)\
            .drop(['year', 'month'], axis=1)\
            .reset_index()\
            .sort_values(['model','scenario'])\
            .reset_index(drop=True)

    df2.to_csv(os.path.join(output_path, 'tas_fulldomain_decadal_annual_mean_alldata_melted.csv'))

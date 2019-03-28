# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# extract point profiles from SNAP 2km data -- output as decadal means
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def list_data( path ):
	l = glob.glob(os.path.join( path, '*.tif' ))
	split_fn = [ os.path.basename(i).split('.')[0].split('_') for i in l ]

	if len( split_fn[0] ) == 7:
		colnames = ['variable', 'metric', 'units', 'model', 'scenario','month','year']	
	else:
		colnames = ['variable', 'metric', 'project', 'units', 'model', 'scenario','month','year']

	df = pd.DataFrame( split_fn, columns=colnames )
	df.month = df.month.astype(int)
	df.year = df.year.astype(int)
	df['fn'] = l
	out_df = df.sort_values(['year', 'month'])
	return out_df['fn'].tolist()

def extract_data( fn, row, col ):
	with rasterio.open( fn ) as rst:
		arr = rst.read(1)
	return arr[ row,col ]

def run_extraction( files, row, col ):
	# multiprocess
	f = partial(extract_data, row=row, col=col)
	pool = mp.Pool( ncpus )
	extracted = pool.map( f, files )
	pool.close()
	pool.join()
	pool = None
	return extracted

def get_rowcol_from_point( x, y, transform ):
	# get the row col using the affine transform
	col, row = ~transform * (x, y)
	col, row = int(col), int(row)
	return row, col

def make_melted( dat, time_index, variable, model, scenario ):
	# prep a data frame
	df = pd.DataFrame( dat ).copy()
	df['year'] = [year for month, year in time_index]
	df['month'] = [month for month, year in time_index]
	# melt it
	melted = df.melt(id_vars=['year', 'month'],var_name='community',value_name=variable)
	# add in some other columns that will be useful when 
	#	concatenating the group melted dataframes later on...
	melted['scenario'] = scenario
	melted['model'] = model
	return melted

def run_group( model, scenario, files_dict, rowcols ):
	names = rowcols.index.tolist()
	variables = list(files_dict.keys())
	# extract the data
	extracted = {variable:{names[idx]:run_extraction( files_dict[variable], rowcol[0], rowcol[1] ) 
					for idx,rowcol in enumerate(rowcols)} for variable in variables}
	# make year_list
	files = files_dict[variables[0]] # grab the first one.  It is assumed that variables within a group have the same time dimension
	years = int(files[0].split('.')[0].split('_')[-1]), int(files[-1].split('.')[0].split('_')[-1])
	all_years = np.repeat(np.arange(years[0], years[1]+1 ), 12)
	all_months = np.concatenate([np.arange(1,13) for i in np.unique(all_years)])
	dates = list(zip(all_months,all_years))

	# melt each of the variables
	melted_data = [make_melted(extracted[v],dates,v,model,scenario) for v in variables]
	return melted_data


if __name__ == '__main__':
	import os, glob, pyproj, itertools
	import numpy as np
	import rasterio
	from rasterio.features import rasterize
	import pandas as pd
	import multiprocessing as mp
	from shapely.geometry import Point
	from functools import partial
	
	base_path = '/workspace/Shared/Tech_Projects/DeltaDownscaling/project_data/downscaled_10min'
	output_path = '/workspace/Shared/Tech_Projects/NWT_CommCharts_MinesApp/project_data/communities_extracted'
	ncpus = 63
	communities_fn = '/workspace/Shared/Tech_Projects/NWT_CommCharts_MinesApp/project_data/SNAP_comm_charts_export_20160926_fix_021119.csv'
	minesites_fn = '/workspace/Shared/Tech_Projects/NWT_CommCharts_MinesApp/project_data/minesites.csv'
	
	models = ['5ModelAvg','GFDL-CM3','GISS-E2-R','IPSL-CM5A-LR','MRI-CGCM3','NCAR-CCSM4']
	scenarios = ['historical','rcp45','rcp60','rcp85']
	variables = ['tas','pr']

	# prepare the points for use in extraction of profiles
	communities = pd.read_csv( communities_fn )
	communities = communities[communities.region == 'Northwest Territories']
	minesites = pd.read_csv( minesites_fn )

	# get the unique points values to use in extractions
	lonlats = communities.groupby('community').first()[['latitude','longitude']]
	lonlats_mines = minesites[['Latitude', 'Longitude']]
	lonlats_mines.index = minesites['Name']
	lonlats_mines.columns = ['latitude','longitude']
	lonlats = pd.concat([lonlats, lonlats_mines])

	# lets make some arguments to use in processing
	args = []
	for model, scenario in itertools.product(models, scenarios):
		variables_dict = {}
		for variable in variables:
			data_path = os.path.join( base_path, model, scenario, variable )
			variables_dict[variable] = list_data( data_path )

		args = args + [{'model':model, 'scenario':scenario, 'files_dict':variables_dict}]

	# lets use a sample file for its affine transform and compute the row/col locations of the points
	with rasterio.open( args[0]['files_dict'][variables[0]][0] ) as tmp:
		meta = tmp.meta

	# compute row col locations
	projected_pts = lonlats.apply(lambda x: pyproj.Proj(init='EPSG:3338')(x.longitude,x.latitude), axis=1)
	rowcols = projected_pts.apply(lambda x: get_rowcol_from_point( x[0], x[1], transform=meta['transform']) )
	
	# update the args with the rowcols
	_ = [i.update(rowcols=rowcols) for i in args]

	# run the extractions for each of the groups in serial
	all_extracted = {' '.join([kw['model'],kw['scenario']]):run_group( **kw ) for kw in args}

	print('WRITING TO CSVS')
	out = {}
	for key in list(all_extracted.keys()):
		model, scenario = str(key).split()
		tas,pr = all_extracted[key]
		tas['pr'] = pr['pr']
		tas[ tas == -9999 ] = np.nan

		# make decadals
		comm_list = []
		for community, sub_df in tas.groupby('community'):
			# group it and figure out the full decades
			decades_grouper = [str(month)+'-'+str(year)[:3]+'0' for year,month in zip(sub_df.year, sub_df.month)]
			full_decades = np.unique([i.split('-')[1] for i,j in zip(*np.unique(decades_grouper, return_counts=True)) if j == 10]).astype(int)
			decadal_avg = sub_df.groupby(decades_grouper).mean()
			
			# build the output 'melted' dataframe
			monyear = pd.DataFrame([ i.split('-') for i in decadal_avg.index.tolist() ], columns=['month','year']).astype(int)
			decadal_avg['month'] = monyear.month.tolist()
			decadal_avg['year'] = monyear.year.tolist()
			decadal_avg = decadal_avg.sort_values(['year','month']).reset_index(drop=True)
			decadal_avg['scenario'] = scenario
			decadal_avg['model'] = model
			decadal_avg['community'] = community

			# slice it to only the full decades.
			decadal_avg = decadal_avg[(decadal_avg.year >= full_decades.min()) & (decadal_avg.year <= full_decades.max())]
			comm_list = comm_list + [decadal_avg]

		out[key] = pd.concat(comm_list).reset_index(drop=True)
	
	# now stack all the models for a given scenario	
	for scenario in scenarios:
		keylist = [key for key in list(out.keys()) if scenario in key]
		out_df = pd.concat([out[key] for key in keylist])
		out_df['tas'] = out_df['tas'].round(1)
		out_df['pr'] = out_df['pr'].round(0)
		out_fn = os.path.join( output_path, 'tas_pr_nwt_decadal_mean_{}_melted.csv'.format(scenario))
		out_df.to_csv( out_fn )

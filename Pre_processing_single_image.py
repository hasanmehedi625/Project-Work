from functions import *
import os

raster_path = r"input_data_folder\TIFs_folder\LC24_CC_spokane.tif"
csv_paths = [r'input_data_folder\CSVs_folder\Data1(in).csv',
             r'input_data_folder\CSVs_folder\Data2(in).csv']
lon_cols = ['LONGITUDE', 'longitude']
lat_cols = ['LATITUDE', 'latitude']
labels = ['Dataset 1', 'Dataset 2']

csvs = load_csvs(csv_paths)
csvs = [df.sample(n=min(100, len(df))) for df in csvs]
raster = load_raster(raster_path)

x_coords, y_coords = transform_coords(csvs, lon_cols, lat_cols, raster.crs)

plot_points_on_raster(raster, x_coords, y_coords, labels,
                      save_path='output_folder/Canopy_Cover.png')

raster.close()
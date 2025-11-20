from functions import *
import os
mymaps = {
    'CanopyCover': r'input_data_folder\TIFs_folder\LC24_CC_spokane.tif',
    'Aspect': r'input_data_folder\TIFs_folder\LC20_Asp_spokane.tif',
    'Elevation': r'input_data_folder\TIFs_folder\LC20_Elev_spokane.tif',
    'SlopeD': r'input_data_folder\TIFs_folder\LC20_SlpD_spokane.tif',
    'CanopyBulkDensity': r'input_data_folder\TIFs_folder\LC24_CBD_spokane.tif',
    'CanopyBaseHeight': r'input_data_folder\TIFs_folder\LC24_CBH_spokane.tif',
    'CanopyHeight': r'input_data_folder\TIFs_folder\LC24_CH_spokane.tif',
    '40FireBehaviorFuel': r'input_data_folder\TIFs_folder\LC24_F40_spokane.tif',
    'PopDensity': r'input_data_folder\TIFs_folder\PopDen_spokane.tif',
    'BuildingDensity': r'input_data_folder\TIFs_folder\BuildingDensity_spokane.tif',
    'HUDen': r'input_data_folder\TIFs_folder\HUDen_spokane.tif',
}
csv_paths = [r'input_data_folder\CSVs_folder\Data1(in).csv',
             r'input_data_folder\CSVs_folder\Data2(in).csv']
lon_cols = ['LONGITUDE', 'longitude']
lat_cols = ['LATITUDE', 'latitude']
labels = ['Dataset 1', 'Dataset 2']

csvs = load_csvs(csv_paths)
csvs = [df.sample(n=min(100, len(df))) for df in csvs]

df1, df2 = load_csvs(csv_paths)
print(f"Data1: {len(df1)} | Data2: {len(df2)}")

df2 = expand_data(df2, lon_cols[1], lat_cols[1], seed=42)
print(f"Data2 expanded: {len(df2)}")

for name, path in mymaps.items():
    raster = load_raster(path)
    df1[name] = extract_raster_values(df1, raster, lon_cols[0], lat_cols[0])
    df2[name] = extract_raster_values(df2, raster, lon_cols[1], lat_cols[1])
    raster.close()

os.makedirs('output_folder', exist_ok=True)
df1.to_csv('output_folder/Data1(out).csv', index=False)
df2.to_csv('output_folder/Data2(out).csv', index=False)

for map_name, raster_path in mymaps.items():
    raster = load_raster(raster_path)
    x_coords, y_coords = transform_coords(csvs, lon_cols, lat_cols, raster.crs)
    plot_points_on_raster(raster, x_coords, y_coords, labels,
                          save_path=f'output_folder/{map_name}.png')
    raster.close()
    print(f'{map_name}.png')
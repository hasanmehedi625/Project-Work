from functions import *
import os
import pandas as pd

weather_folder = r'input_data_folder\Weather_data_folder'
csv_paths = [r'input_data_folder\CSVs_folder\Data1(in) (1).csv',
             r'input_data_folder\CSVs_folder\Data2(in).csv']
lon_cols = ['LONGITUDE', 'longitude']
lat_cols = ['LATITUDE', 'latitude']

df1 = pd.read_csv(csv_paths[0])
df2 = pd.read_csv(csv_paths[1])
print(f"\nLoaded Data1: {len(df1)} rows | Data2: {len(df2)} rows")

if 'year' not in df1.columns or 'DOY' not in df1.columns:
    df1 = generate_random_dates(df1, year_range=(2015, 2023), seed=42)
else:
    print(f"Data1 dates: {df1['year'].min()}-{df1['year'].max()}")

year_min, year_max = int(df1['year'].min()), int(df1['year'].max())
df2 = generate_random_dates(df2, year_range=(year_min, year_max), seed=42)
print(f"Generated dates: {year_min}-{year_max}")

weather_datasets = load_all_weather_data(weather_folder)
print(f"Loaded {len(weather_datasets)} datasets: {list(weather_datasets.keys())}")

if len(weather_datasets) == 0:
    exit()

print("\nData1:")
df1 = sample_weather_parameters(df1, weather_datasets, lon_cols[0], lat_cols[0])

print("\nData2:")
df2 = sample_weather_parameters(df2, weather_datasets, lon_cols[1], lat_cols[1])

os.makedirs('output_folder', exist_ok=True)
df1.to_csv('output_folder/Data1_with_weather.csv', index=False)
df2.to_csv('output_folder/Data2_with_weather.csv', index=False)

print(f"\nData1: {len(df1)} rows, {len(df1.columns)} columns")
print(f"Data2: {len(df2)} rows, {len(df2.columns)} columns")

weather_cols = list(weather_datasets.keys())
print(df1[weather_cols].describe())
print(df2[weather_cols].describe())

for col in weather_cols:
    m1 = df1[col].isnull().sum()
    m2 = df2[col].isnull().sum()
    print(f"  {col}: Data1={m1} ({100*m1/len(df1):.1f}%) | Data2={m2} ({100*m2/len(df2):.1f}%)")
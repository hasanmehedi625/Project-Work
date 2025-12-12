import rasterio
import pandas as pd
from rasterio.windows import from_bounds
from pyproj import Transformer
import matplotlib.pyplot as plt
import numpy as np
import os

import xarray as xr
import numpy as np
from datetime import datetime, timedelta
import glob
def load_raster(path):
    return rasterio.open(path)

def load_csvs(paths):
    return [pd.read_csv(p) for p in paths]

def sample_points(dfs, n=100):
    return [df.sample(min(n, len(df))) for df in dfs]

def transform_coords(dfs, lon_cols, lat_cols, target_crs):
    transformer = Transformer.from_crs("EPSG:4326", target_crs, always_xy=True)
    x_list, y_list = [], []
    for df, lon_col, lat_col in zip(dfs, lon_cols, lat_cols):
        x, y = transformer.transform(df[lon_col].values, df[lat_col].values)
        x_list.append(x)
        y_list.append(y)
    return x_list, y_list

def plot_points(map_obj, dataframe):
    plt.figure()
    plt.show()

def expand_data(df, lon_col, lat_col, seed=42):
    np.random.seed(seed)
    n = int(len(df) * 0.5)
    new_df = pd.DataFrame({
        lon_col: np.random.uniform(df[lon_col].min(), df[lon_col].max(), n),
        lat_col: np.random.uniform(df[lat_col].min(), df[lat_col].max(), n)
    })
    return pd.concat([df, new_df], ignore_index=True)

def extract_raster_values(df, raster, lon_col, lat_col):
    from pyproj import Transformer

    lons = df[lon_col].values
    lats = df[lat_col].values

    transformer = Transformer.from_crs("EPSG:4326", raster.crs, always_xy=True)
    xs, ys = transformer.transform(lons, lats)

    rows, cols = rasterio.transform.rowcol(raster.transform, xs, ys)
    data = raster.read(1)

    values = [data[r, c] if 0 <= r < data.shape[0] and 0 <= c < data.shape[1] else np.nan
              for r, c in zip(rows, cols)]
    return values

def add_raster_parameters(df, rasters_dict, lon_col, lat_col):
    for name, path in rasters_dict.items():
        raster = load_raster(path)
        df[name] = extract_raster_values(df, raster, lon_col, lat_col)
        raster.close()
    return df

def plot_points_on_raster(raster, x_coords, y_coords, labels, save_path=None,
                          title=None, point_size=50, alpha=0.7):
    fig, ax = plt.subplots(figsize=(12, 10))

    raster_data = raster.read(1, masked=True)
    extent = [raster.bounds.left, raster.bounds.right,
              raster.bounds.bottom, raster.bounds.top]
    im = ax.imshow(raster_data, cmap='YlGn', extent=extent, alpha=0.8)

    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label='Raster Value')

    colors = ['#FF4444', '#4444FF', '#FF8C00', '#9932CC']
    for i, (x, y, label) in enumerate(zip(x_coords, y_coords, labels)):
        ax.scatter(x, y, c=colors[i % len(colors)], s=point_size,
                   alpha=alpha, label=label, edgecolors='white', linewidth=0.8)

    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    ax.set_title(title or 'Points on Raster', fontsize=14, fontweight='bold')
    ax.set_xlabel('Easting (m)', fontsize=11)
    ax.set_ylabel('Northing (m)', fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()

    if save_path:
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f" Saved: {save_path}")
    else:
        plt.show()
    plt.close()




def load_weather_netcdf(file_path):
    try:
        ds = xr.open_dataset(file_path)
        return ds
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None


def doy_to_date(year, doy):
    try:
        return datetime(int(year), 1, 1) + timedelta(days=int(doy) - 1)
    except:
        return None


def extract_weather_value(ds, lon, lat, date, variable_name):
    try:
        np_date = np.datetime64(date)
        value = ds[variable_name].sel(lon=lon, lat=lat, day=np_date, method='nearest').values
        return float(value)
    except:
        return np.nan


def sample_weather_parameters(df, weather_datasets, lon_col, lat_col, year_col='year', doy_col='DOY'):
    df_copy = df.copy()

    for param_name, (ds, var_name) in weather_datasets.items():
        print(f"  Sampling {param_name}...")
        values = []

        for idx, row in df_copy.iterrows():
            try:
                date = doy_to_date(int(row[year_col]), int(row[doy_col]))
                if date:
                    value = extract_weather_value(ds, float(row[lon_col]), float(row[lat_col]), date, var_name)
                    values.append(value)
                else:
                    values.append(np.nan)
            except:
                values.append(np.nan)

        df_copy[param_name] = values
        valid = df_copy[param_name].notna().sum()
        print(f"    Valid: {valid}/{len(df_copy)} ({100 * valid / len(df_copy):.1f}%)")

    return df_copy


def generate_random_dates(df, year_range=(2015, 2023), seed=42):
    np.random.seed(seed)
    df_copy = df.copy()
    df_copy['year'] = np.random.randint(year_range[0], year_range[1] + 1, len(df_copy))
    df_copy['DOY'] = np.random.randint(1, 366, len(df_copy))
    return df_copy


def load_all_weather_data(weather_folder):
    file_patterns = {
        'Precip': ('*pr*.nc', 'precipitation_amount'),
        'RH': ('*rmax*.nc', 'relative_humidity'),
        'Tmax': ('*tmmx*.nc', 'air_temperature'),
        'WindSpeed': ('*vs*.nc', 'wind_speed'),
    }

    weather_datasets = {}

    for param_name, (pattern, var_name) in file_patterns.items():
        files = glob.glob(os.path.join(weather_folder, pattern))
        if files:
            ds = load_weather_netcdf(files[0])
            if ds is not None:
                if var_name in ds.data_vars:
                    weather_datasets[param_name] = (ds, var_name)
                elif len(ds.data_vars) > 0:
                    actual_var = list(ds.data_vars)[0]
                    weather_datasets[param_name] = (ds, actual_var)

    return weather_datasets
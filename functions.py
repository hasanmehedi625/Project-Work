import rasterio
import pandas as pd
from rasterio.windows import from_bounds
from pyproj import Transformer
import matplotlib.pyplot as plt
import numpy as np
import os

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
        print(f"✓ Saved: {save_path}")
    else:
        plt.show()

    plt.close()
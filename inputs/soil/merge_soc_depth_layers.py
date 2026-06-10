"""
Merges the shallow, medium, and deep restrictive-depth soil organic carbon
rasters into a single seamless layer raster. NoData and zero cells in one
raster are filled with values from the others during the merge.
"""

import rasterio
from rasterio.merge import merge
import numpy as np

# File paths and output file path
filepath_root = 'path/to/SOLUS/SOC/'
filepaths = [f'{filepath_root}deep/soc_gm2_19.125.tif',
             f'{filepath_root}medium/soc_gm2_13.5.tif',
             f'{filepath_root}shallow/soc_gm2_5.875.tif']
stitched_file = f'{filepath_root}layer1/layer1_humusC_gm2.tif'

# Define the NoData value
nodata_value = -9999
crs = 'EPSG:26910'

# Open and process each raster
datasets = []
for fp in filepaths:
    with rasterio.open(fp) as dataset:
        # Read the data
        data = dataset.read(1).astype('float32')

        # Convert NoData values and zeros to NaN
        data[(data == nodata_value) | (data == 0)] = np.nan

        # Create an in-memory raster to store modified data
        memfile = rasterio.io.MemoryFile()
        masked_dataset = memfile.open(
            driver='GTiff',
            height=dataset.height,
            width=dataset.width,
            count=1,
            dtype='float32',
            crs=dataset.crs,
            transform=dataset.transform,
            nodata=np.nan
        )
        masked_dataset.write(data, 1)
        datasets.append(masked_dataset)

# Merge the rasters, allowing NaN values to be replaced with data from other rasters
merged_raster, output_transform = merge(datasets)

# Replace NaN values with the desired NoData value
merged_raster = np.nan_to_num(merged_raster, nan=nodata_value)

# Copy metadata from the first raster
meta = datasets[0].meta.copy()
meta.update({
    'driver': 'GTiff',
    'height': merged_raster.shape[1],
    'width': merged_raster.shape[2],
    'transform': output_transform,
    'crs': crs,
    'nodata': nodata_value
})

# Write the merged raster to the output file
with rasterio.open(stitched_file, 'w', **meta) as dest:
    dest.write(merged_raster[0], 1)

# Close datasets
for dataset in datasets:
    dataset.close()

print(f"Stitched raster saved to {stitched_file}")

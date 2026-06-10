"""
Interpolates SOLUS soil property rasters from the depths at which data are
published (0-150 cm) to the depths required by the VELMA soil layers. Performs
per-pixel linear interpolation between the nearest valid depths above and
below each target depth.
"""

import numpy as np
import rasterio
from scipy.interpolate import interp1d

# Define the depths at which rasters are available and the target depths for interpolation
known_depths = [0, 5, 15, 30, 60, 100, 150]  # Depths of available data in cm
target_depths = [5.875, 17.625, 29.375, 41.125, 13.5, 40.5, 67.5, 94.5,
                 19.125, 51.75, 90.0, 128.25]  # Depths of desired data in cm
nodata_value = -9999  # Define your NoData value to make sure it isn't used in the interpolation
parameter = 'soc'  # Must match folder name

# Read raster data for known depths
rasters = []
for depth in known_depths:
    with rasterio.open(f'path/to/SOLUS/{parameter}/{parameter}_{depth}_Puget_Sound_clipped.tif') as src:
        data = src.read(1)
        data = np.where(data == nodata_value, np.nan, data)  # Replace NoData values with np.nan
        data = np.where(data == 0, np.nan, data)  # Replace zero values with np.nan
        rasters.append(data)

# Stack rasters to have a 3D array of shape (len(known_depths), height, width)
rasters = np.array(rasters)

# Perform interpolation for each pixel
interpolated_data = np.zeros((len(target_depths), rasters.shape[1], rasters.shape[2]))

# Loop over each pixel and apply interpolation
for i in range(rasters.shape[1]):  # Loop over rows
    for j in range(rasters.shape[2]):  # Loop over columns
        # Extract values for the pixel at different depths
        data_values = rasters[:, i, j]

        # Ignore pixels where all values are NaN
        if np.all(np.isnan(data_values)):
            interpolated_data[:, i, j] = np.nan
        else:
            # Perform cubic spline interpolation, skipping NaN values
            valid_mask = ~np.isnan(data_values)
            valid_depths = np.array(known_depths)[valid_mask]
            valid_data = data_values[valid_mask]

            # Check if we have at least two valid points in the set
            if len(valid_data) >= 2:
                for k, target_depth in enumerate(target_depths):
                    # Find the valid depths on either side of the target_depth
                    valid_below = valid_depths[valid_depths <= target_depth]
                    valid_above = valid_depths[valid_depths >= target_depth]

                    # Check if we have points both below and above the target_depth
                    if len(valid_below) > 0 and len(valid_above) > 0:
                        depth_below = valid_below[-1]  # Closest valid depth below
                        depth_above = valid_above[0]  # Closest valid depth above

                        # Get corresponding data points
                        value_below = valid_data[valid_depths == depth_below][0]
                        value_above = valid_data[valid_depths == depth_above][0]

                        # If both values are valid, interpolate
                        if not np.isnan(value_below) and not np.isnan(value_above):
                            interpolate = interp1d([depth_below, depth_above], [value_below, value_above],
                                                   kind='linear')
                            interpolated_data[k, i, j] = interpolate(target_depth)
                        else:
                            interpolated_data[k, i, j] = np.nan  # Cannot interpolate
                    else:
                        interpolated_data[k, i, j] = np.nan  # Not enough valid neighbors
            else:
                interpolated_data[:, i, j] = np.nan  # Not enough data to interpolate

# Write interpolated rasters to new files
for idx, target_depth in enumerate(target_depths):
    with rasterio.open(
        f'path/to/SOLUS/{parameter}/interpolated_{parameter}_{target_depth}.tif',
        'w',
        driver='GTiff',
        height=rasters.shape[1],
        width=rasters.shape[2],
        count=1,
        dtype=rasterio.float32,  # Assume values are floats
        crs=src.crs,
        transform=src.transform,
        nodata=nodata_value  # Write back the NoData value in the output
    ) as dst:
        dst.write(interpolated_data[idx], 1)

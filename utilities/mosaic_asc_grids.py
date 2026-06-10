"""
Stitches all .asc rasters in a directory into a single combined grid by
stacking and overlaying them. Used to assemble tiled coverage (e.g. land cover
tiles) into one Puget Sound-wide grid. See merge_rasters.py for the
rasterio.merge-based mosaic version.
"""

import rasterio
import os
import numpy as np

# Define the directory path
directory = 'path/to/PSIMF_GIS/Raster/Land_Cover'
out_file = 'Puget_Sound_Land_Coverage.asc'
# file_names = ['Spatial_AgBiomassCarbon_ALL_1_2008_1.asc', 'Spatial_CoverAge_ALL_1_2008_1.asc', 'Spatial_WATER_STORED_ALL_1_2008_1.asc', 'Spatial_HUMUS_ALL_1_2008_1.asc']

# Iterate over subdirectories in the specified directory
# for full_file_name in file_names:
    # Create an empty list to store the raster data
all_data = []
metadata = None
for raster_file in os.listdir(directory):
    file_path = os.path.join(directory, raster_file)
        
    # Read the raster file
    with rasterio.open(file_path) as asc_file:
        # Read the first band (assuming single band)
        data = asc_file.read(1)
        
        # Filter out values less than or equal to zero by marking them as NaN
        # data[data <= 0] = np.nan
        
        # Append the filtered data
        all_data.append(data)
        
        # Store the metadata for the first file (assumes all have same metadata)
        if metadata is None:
            metadata = asc_file.meta
            metadata.update({
                'driver': 'AAIGrid',  # Format for .asc
                'crs': 'EPSG:26910',  # Include the CRS directly
            })

# Composite the rasters:
# Start with the first raster and then fill in missing (NaN) pixels with valid values from subsequent rasters.
# This approach ensures that valid data isn't overwritten by NaN values.
composite = np.copy(all_data[0])
for arr in all_data[1:]:
    # For each pixel: if composite has NaN and the new array has a valid value, use that valid value.
    composite = np.where(np.isnan(composite) & ~np.isnan(arr), arr, composite)

# Save the composite into a new raster file
output_file = os.path.join(directory, out_file)
with rasterio.open(output_file, 'w', **metadata) as dst:
    dst.write(composite, 1)  # Write to the first band

print(f"Rasters stitched and saved to {output_file}")

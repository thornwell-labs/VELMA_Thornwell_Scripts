"""
Cleans soil type .asc grids by replacing any cell value not in the allowed set
of soil type IDs with a default value, writing the corrected grids to an
output folder. Fixes stray/invalid classes from soil map processing.
"""

import os
import rasterio
import numpy as np

# Configuration
input_directory = 'path/to/VELMA_Watersheds/soil_maps'  # Change this to your folder path
output_directory = 'path/to/VELMA_Watersheds/soil_maps_fixed'  # Where modified files will be saved
allowable_values = [12, 17, 24, 112, 117, 124, 212, 217, 224]
replacement_value = 24

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Function to write data as ASCII grid (.asc)
def write_asc(output_path, data, profile):
    # Modify the profile to use AAIGrid format (ASCII Grid)
    profile.update(driver='AAIGrid', dtype='int32', count=1)

    # Write the modified data to an ASCII grid file
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(data, 1)

# Loop through all ASCII files and process
for filename in os.listdir(input_directory):
    if filename.endswith('.asc'):  # Ensure we're processing .asc files
        input_path = os.path.join(input_directory, filename)
        output_path = os.path.join(output_directory, filename)

        with rasterio.open(input_path) as src:
            raster_data = src.read(1)  # Read first band
            profile = src.profile

        # Replace non-allowable values with the replacement value
        modified_data = np.where(np.isin(raster_data, allowable_values), raster_data, replacement_value)

        # Write the modified data to an ASCII grid
        write_asc(output_path, modified_data, profile)

        print(f"Processed and saved as .asc: {filename}")

print("Batch processing complete.")

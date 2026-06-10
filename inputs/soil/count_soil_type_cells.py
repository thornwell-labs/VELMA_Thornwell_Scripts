"""
Counts the number of raster cells belonging to each soil type in a soil types
map (.tif) and prints the per-type cell counts. Useful for checking the
distribution of soil classes produced by soil_classifier.py.
"""

import numpy as np
from collections import Counter
import rasterio

output_tif = 'path/to/SOLUS/soil_types_map.tif'

# Load the saved soil types map
with rasterio.open(output_tif) as soil_types_src:
    soil_types_data = soil_types_src.read(1)

# Get the unique values and their counts
unique, counts = np.unique(soil_types_data, return_counts=True)

# Print results as a dictionary for easier reading
soil_type_counts = dict(zip(unique, counts))
for soil_type, count in soil_type_counts.items():
    print(f"Soil type {soil_type}: {count} cells")

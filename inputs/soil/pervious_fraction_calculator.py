"""
Takes a land cover .asc file and converts it to percent pervious to use in setPermeabilityFraction
"""

import rasterio
import numpy as np

# Define these file paths
lc_filename = ''
pervious_filename = ''

# ----- Shouldn't need to edit anything below this line -----

def lc_to_pervious_frac(land_cover_path, pervious_path):
    # 21 through 24 are the developed land cover types.
    # The associated values are the pervious fraction (average of the NLCD ranges, converted from percent impervious)
    # Source: https://www.mrlc.gov/data/legends/national-land-cover-database-class-legend-and-description
    lc_to_pervious_dict = {
        21: 0.9,
        22: 0.655,
        23: 0.355,
        24: 0.1
    }

    # Open the .asc with rasterio and save the header data (profile) for later use
    with rasterio.open(land_cover_path) as src:
        data = src.read(1)
        profile = src.profile

    # Change the dtype of the profile to float, because the original data was integer and the new data is float
    profile.update(dtype=rasterio.float32)

    # Default pervious fraction is 1.0 (fully pervious)
    default_value = 1.0

    # Look up each value in the .asc and replace with the value in lc_to_pervious_frac, if applicable; else use default value
    mapped_data = np.vectorize(lc_to_pervious_dict.get)(data, default_value)
    rounded_data = np.round(mapped_data, 3)

    # Write the mapped data to a new .asc
    with rasterio.open(pervious_path, 'w', **profile) as dst:
        dst.write(rounded_data, 1)



lc_to_pervious_frac(lc_filename, pervious_filename)
    
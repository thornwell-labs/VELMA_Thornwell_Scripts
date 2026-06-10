"""
Accepts the land cover raster and creates groups based on the expected carbon-to-nitrogen ratio.
Output is a .tif file with the C/N ratio values of each cell.
"""

import rasterio
import numpy as np


# Define paths to NLCD land cover file and desired output path
land_cover_tif = 'path/to/PSIMF_GIS/Raster/NLCD_LEMMA_LandCover30m_PugetSound_clipped.tif'
out_tif = 'path/to/SOLUS/cn_ratio.tif'

# Define desired carbon-to-nitrogen ratios for each  land cover class
c_n_ratios = {12: [11, 12, 24, 82, 71, 90],
              17: [7, 8, 9, 21, 22, 23, 31],
              24: [5, 6, 42, 52, 43]}

ratio_lookup = {}
for ratio, classes in c_n_ratios.items():
    for cls in classes:
        ratio_lookup[cls] = ratio

with rasterio.open(land_cover_tif) as lc_tif:
    land_cover_data = lc_tif.read(1)
    c_n_ratio_data = np.zeros(land_cover_data.shape, dtype=np.float32)

    # Map land cover classes to C/N ratios
    for cls, ratio in ratio_lookup.items():
        c_n_ratio_data[land_cover_data == cls] = ratio

    # Define metadata for output raster
    ratio_profile = lc_tif.profile
    ratio_profile.update(dtype=rasterio.float32, count=1, compress='lzw')

    # Save C/N ratio raster
    with rasterio.open(out_tif, 'w', **ratio_profile) as dst:
        dst.write(c_n_ratio_data, 1)

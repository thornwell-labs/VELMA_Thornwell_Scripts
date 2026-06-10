"""
Creates a humus nitrogen reduction-fraction raster from an NLCD land cover
raster. Each land cover class is assigned a multiplier (0.1-1.0) representing
the expected reduction in humus nitrogen for that cover type; the output .tif
is later applied to nitrogen layers with multiply_asc_files.py.
"""

import rasterio
import numpy as np
from rasterio.warp import reproject, Resampling

land_cover_tif = r'path\to\PSIMF_GIS\Raster\NLCD_LEMMA_LandCover30m_PugetSound_clipped.tif'

reduction_fractions = {0.5: [31],
                       0.4: [21],
                       0.3: [11, 12, 22],
                       0.2: [23],
                       0.1: [24],
                       1: [5, 6, 7, 8, 9, 42, 43, 52, 81, 82, 71, 90]
                      }

fraction_lookup = {}
for fraction, classes in reduction_fractions.items():
    for cls in classes:
        fraction_lookup[cls] = fraction

with rasterio.open(land_cover_tif) as lc_tif:
    land_cover_data = lc_tif.read(1)
    reduction_data = np.zeros(land_cover_data.shape, dtype=np.float32)

    # Map land cover classes to C/N ratios
    for cls, fraction in fraction_lookup.items():
        reduction_data[land_cover_data == cls] = fraction

    # Define metadata for output raster
    ratio_profile = lc_tif.profile
    ratio_profile.update(dtype=rasterio.float32, count=1, compress='lzw')

    # Save C/N ratio raster
    reduction_tif = r'path\to\SOLUS\nitrogen_reduction_fractions.tif'
    with rasterio.open(reduction_tif, 'w', **ratio_profile) as dst:
        dst.write(reduction_data, 1)

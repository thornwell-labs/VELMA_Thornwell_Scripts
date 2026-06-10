"""
Mosaics all .asc rasters in a directory into a single combined grid using
rasterio.merge, writing the result as an ASCII grid in NAD83 / UTM 10N. Used
to assemble tiled inputs (e.g. soil tiles) into one Puget Sound-wide grid.
"""

import rasterio
from rasterio.merge import merge
import os
# import numpy as np

directory = 'path/to/PSIMF_GIS/Raster/Soil'
out_file = 'Puget_Sound_Soils.asc'

rasters = []
for fname in os.listdir(directory):
    if fname.endswith(".asc"):
        path = os.path.join(directory, fname)
        src = rasterio.open(path)
        rasters.append(src)

# Merge all rasters into a single mosaic
mosaic, out_transform = merge(rasters)

# mosaic is shape (1, height, width), so extract the band
composite = mosaic[0]

# Use metadata from first raster and update
metadata = rasters[0].meta.copy()
metadata.update({
    "driver": "AAIGrid",
    "height": composite.shape[0],
    "width": composite.shape[1],
    "transform": out_transform,
    "crs": "EPSG:26910",
})

# Save the output
output_file = os.path.join(directory, out_file)
with rasterio.open(output_file, "w", **metadata) as dst:
    dst.write(composite, 1)

print("Mosaic saved:", output_file)

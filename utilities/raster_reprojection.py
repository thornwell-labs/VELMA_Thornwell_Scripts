"""
Reprojects and resamples a source raster to match the grid, extent, and
projection of a reference raster, writing the aligned result as an .asc grid.
As configured it aligns a C/N ratio GeoTIFF to a VELMA humus carbon grid, but
the source and reference rasters can be any pair.
"""

import rasterio
import numpy as np
from rasterio.warp import reproject, Resampling
import os
from pyproj import CRS

# Specify results folder and define coordinate reference system
results_folder = 'path/to/VELMA_Watersheds/Samish/Results/WA_Samish30m_Eliminate_Nitrogen_Fixation_resampled_3'
out_path = 'path/to/VELMA_Watersheds/Samish/Analysis/Nitrogen_Sources/Samish_cn_ratio.asc'
crs = CRS.from_epsg(26910)


carbon_nitrogen_ratio_tif = 'path/to/SOLUS/cn_ratio.tif'

# Search for and select the first humus carbon file
for root, dirs, files in os.walk(results_folder):
        for filename in files:
            if filename.startswith('Spatial_HUMUS'):
                humus_carbon_example = filename
                humus_carbon_example = os.path.join(results_folder, humus_carbon_example)
                break


# Resample the carbon/nitrogen ratio file to match the humus carbon file
with rasterio.open(carbon_nitrogen_ratio_tif) as tif_src:
    src_data = tif_src.read(1)
    src_meta = tif_src.meta.copy()

with rasterio.open(humus_carbon_example) as tif_dst:
    dst_data = tif_dst.read(1)
    dst_meta = tif_dst.meta.copy()
    dst_width = tif_dst.width
    dst_height = tif_dst.height


# Create empty numpy array to dump the resampled data
resampled_data = np.empty((dst_height, dst_width), dtype=src_data.dtype)

reproject(
    source=src_data,
    destination=resampled_data,
    src_transform=src_meta['transform'],
    src_crs = crs,
    dst_transform=dst_meta['transform'],
    dst_crs = crs,
    resampling=Resampling.nearest,
    dst_nodata=24
)

with rasterio.open(out_path, "w", **dst_meta) as dst:
    dst.write(resampled_data, 1)
    
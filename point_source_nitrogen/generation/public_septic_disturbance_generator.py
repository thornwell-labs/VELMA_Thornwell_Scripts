"""
Creates VELMA septic disturbance input grids (.asc) for a watershed by
clipping Puget Sound-wide septic NH4 (g/m^2) and septic water (mm/day) rasters
to the watershed extent. Outputs feed VELMA's disturbance configuration for
public/high-sewer septic scenarios.
"""

import rasterio
from rasterio.windows import from_bounds
import numpy as np

# Specify these inputs - may only need to specify the watershed
watershed = 'Stillaguamish'
watershed_lower = watershed.lower()
asc_extent_file = rf"path\to\VELMA_Watersheds\{watershed}\Data_Inputs30m\o_11_Disturbances\{watershed_lower}_highsewer_septicparcel_points_nh4_additions.asc"
nh4_out_asc = rf"path\to\VELMA_Watersheds\{watershed}\Data_Inputs30m\o_11_Disturbances\{watershed}_Septic_NH4_gm2_Public.asc"
water_out_asc = rf"path\to\VELMA_Watersheds\{watershed}\Data_Inputs30m\o_11_Disturbances\{watershed}_Septic_Water_mmday_Public.asc"


# ---------------------------------------------------------------------- # 

water_tif_file = r"path\to\PSIMF_GIS\Raster\Puget_Sound_NHDV2_Septic_Water_EPSG26910_mmday.tif"
nh4_tif_file = r"path\to\PSIMF_GIS\Raster\Puget_Sound_NHDV2_Septic_NH4_EPSG26910_gm2.tif"
nodata_in = -3.4028234663852885981e+38
nodata_out = -9999

def clip_to_asc_extent(src_tif, extent_asc, out_asc):
    with rasterio.open(extent_asc) as extent_src:
        left, bottom, right, top = extent_src.bounds
        out_transform = extent_src.transform
        out_height = extent_src.height
        out_width = extent_src.width

    with rasterio.open(src_tif) as src:
        window = from_bounds(left, bottom, right, top, transform=src.transform)
        window = window.round_offsets().round_lengths()

        out_image = src.read(
            1,
            window=window,
            boundless=True,
            fill_value=nodata_in
        ).astype(np.float32)

        out_image[out_image == nodata_in] = 0.0

        out_meta = src.meta.copy()
        out_meta.update({
            'driver': 'AAIGrid',
            'height': out_height,
            'width': out_width,
            'transform': out_transform,
            'nodata': nodata_out,
            'dtype': 'float32',
            'count': 1
        })

        with rasterio.open(out_asc, 'w', **out_meta) as dst:
            dst.write(out_image, 1)

clip_to_asc_extent(water_tif_file, asc_extent_file, water_out_asc)
clip_to_asc_extent(nh4_tif_file, asc_extent_file, nh4_out_asc)
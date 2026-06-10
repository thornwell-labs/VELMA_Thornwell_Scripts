"""
Reusable helper that resamples a raster to match a reference raster's grid,
extent, and projection, with selectable resampling method (nearest, bilinear,
cubic). Imported by other scripts such as add_land_cover.py.
"""

import rasterio
from rasterio.warp import reproject, calculate_default_transform, Resampling
import numpy as np

# Mapping of resampling methods
sampling_methods = {
    'nearest': Resampling.nearest,
    'bilinear': Resampling.bilinear,
    'cubic': Resampling.cubic,
}

def resample_raster(input_raster_path, reference_raster_path, output_raster_path, nodata=-9999, method='bilinear', default_crs='EPSG:26910'):
    # Open the reference raster to get the desired transform, shape, and CRS
    with rasterio.open(reference_raster_path) as ref_raster:
        ref_transform = ref_raster.transform
        if ref_raster.crs == None:
            ref_crs = default_crs
        else:
            ref_crs = ref_raster.crs
        ref_width = ref_raster.width
        ref_height = ref_raster.height
        ref_bounds = ref_raster.bounds
        ref_nodata = ref_raster.nodata if ref_raster.nodata is not None else nodata

    # Open the raster that needs to be resampled
    with rasterio.open(input_raster_path) as src:
        src_transform = src.transform
        if src.crs == None:
            src.crs = default_crs
        else:
            src_crs = src.crs
        src_nodata = src.nodata if src.nodata is not None else nodata
        src_data = src.read(1)  # Assume single-band raster for simplicity

        # Create an empty array for the resampled data
        resampled_data = np.empty((ref_height, ref_width), dtype=src_data.dtype)

        # Reproject the raster to match the reference raster
        reproject(
            source=src_data,
            destination=resampled_data,
            src_transform=src_transform,
            src_crs=src_crs,
            dst_transform=ref_transform,
            dst_crs=ref_crs,
            dst_nodata=nodata,
            resampling=sampling_methods[method],
        )

    # Save the resampled raster
    with rasterio.open(
        output_raster_path,
        'w',
        driver='AAIGrid',
        height=ref_height,
        width=ref_width,
        count=1,
        dtype=resampled_data.dtype,
        crs=ref_crs,
        transform=ref_transform,
        nodata=nodata,
    ) as dst:
        dst.write(resampled_data, 1)

if __name__ == "__main__":
    # Define paths
    dem_raster = 'path/to/VELMA_Watersheds/Samish/Data_Inputs30m/m_1_DEM/Samish30m_DredgeMask_EEX.asc'
    psimf_raster = 'path/to/SOLUS/nitrogen_reduction_fractions.tif'
    output_raster = 'path/to/VELMA_Watersheds/PSIMF_GIS/Raster/Samish_nitrogen_reduction_fractions.tif'

    # Resample raster(s)
    resample_raster(psimf_raster, dem_raster, output_raster, nodata=0, method='nearest')

"""
Converts percent soil organic carbon rasters to g/m^2 using bulk density,
layer thickness, and rock fraction rasters. Processes every interpolated depth
within each restrictive-depth class (shallow/medium/deep).
"""

import rasterio
import numpy as np
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

# List of restrictive depth layers. The first number is the layer thickness.
resdepth_layers = {
    'shallow': ['11.75', '5.875', '17.625', '29.375', '41.125'],
    'medium': ['27.0', '13.5', '40.5', '67.5', '94.5'],
    'deep': ['38.25', '19.125', '51.75', '90.0', '128.25'],
}

for resdepth, layers in resdepth_layers.items():
    layer_thickness = float(layers[0])
    for layer in layers[1:]:
        percent_SOC_tif = f'path/to/SOLUS/SOC/{resdepth}/interpolated_soc_{layer}_clipped.tif'
        output_file = f'path/to/SOLUS/SOC/{resdepth}/soc_gm2_{layer}.tif'
        bulk_density_tif = f'path/to/SOLUS/bulk_density/interpolated_bulk_density_{layer}.tif'
        rock_fraction_tif = f'path/to/SOLUS/rock_fraction/interpolated_rock_fraction_{layer}.tif'

        # Open all the input raster files
        with rasterio.open(percent_SOC_tif, crs='EPSG:26910') as percent_SOC:
            out_shape = (percent_SOC.height, percent_SOC.width)
            transform = percent_SOC.transform
            crs = percent_SOC.crs

            # Reproject bulk density and rock fraction rasters to match percent_SOC
            with rasterio.open(bulk_density_tif) as bulk_density:
                with WarpedVRT(bulk_density, crs=crs, transform=transform, height=out_shape[0], width=out_shape[1],
                               resampling=Resampling.nearest) as vrt:
                    bulk_density_data = vrt.read(1)

            with rasterio.open(rock_fraction_tif) as rock_fraction:
                with WarpedVRT(rock_fraction, crs=crs, transform=transform, height=out_shape[0], width=out_shape[1],
                               resampling=Resampling.nearest) as vrt:
                    rock_fraction_data = vrt.read(1)

            # Read percent_SOC_data after reprojecting others
            percent_SOC_data = percent_SOC.read(1)
            percent_SOC_data = np.where(percent_SOC_data == percent_SOC.nodata, np.nan, percent_SOC_data)
            bulk_density_data = np.where(bulk_density_data == bulk_density.nodata, np.nan, bulk_density_data)
            rock_fraction_data = np.where(rock_fraction_data == rock_fraction.nodata, np.nan, rock_fraction_data)

            # Perform the cell-by-cell calculation using numpy
            # Assume SOC in percent*1000, bulk_density in g/cm^3*100, layer_thickness in cm, rock_fraction in percent
            SOC_g_m2 = ((percent_SOC_data/1000)/100) * (bulk_density_data/100) * layer_thickness * 10**4 * ((100-rock_fraction_data)/100)

            # Write the output to a new raster file
            with rasterio.open(
                    output_file,
                    'w',
                    driver='GTiff',
                    height=percent_SOC.shape[0],
                    width=percent_SOC.shape[1],
                    count=1,
                    dtype=SOC_g_m2.dtype,
                    crs=percent_SOC.crs,
                    nodata=-9999,
                    transform=percent_SOC.transform
            ) as dest:
                dest.write(SOC_g_m2, 1)

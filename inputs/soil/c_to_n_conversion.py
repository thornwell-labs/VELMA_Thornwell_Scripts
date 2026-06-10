"""
Converts soil organic carbon rasters (g/m^2) to nitrogen rasters (g/m^2) for each
of the four VELMA soil layers by dividing carbon by a C/N ratio raster.
The C/N ratio raster is reprojected to match each carbon map before division.
"""

import rasterio
import numpy as np
from rasterio.warp import calculate_default_transform, reproject, Resampling

cn_ratio_tif = r'path\to\SOLUS\cn_ratio.tif'

carbon_maps = [r'path\to\SOLUS\soc\layer1_humusC_gm2.tif',
               r'path\to\SOLUS\soc\layer2_humusC_gm2.tif',
               r'path\to\SOLUS\soc\layer3_humusC_gm2.tif',
               r'path\to\SOLUS\soc\layer4_humusC_gm2.tif']

output_nitrogen_maps = [
    r'path\to\SOLUS\nitrogen\layer1_humusN_gm2.tif',
    r'path\to\SOLUS\nitrogen\layer2_humusN_gm2.tif',
    r'path\to\SOLUS\nitrogen\layer3_humusN_gm2.tif',
    r'path\to\SOLUS\nitrogen\layer4_humusN_gm2.tif'
]

with rasterio.open(cn_ratio_tif) as cn_ratio_tif:
    cn_ratio_data = cn_ratio_tif.read(1)
    cn_ratio_meta = cn_ratio_tif.meta
    cn_transform = cn_ratio_tif.transform
    cn_crs = cn_ratio_tif.crs

    for c_map, n_map in zip(carbon_maps, output_nitrogen_maps):
        with rasterio.open(c_map) as carbon_tif:
            carbon_data = carbon_tif.read(1)
            transform, width, height = calculate_default_transform(cn_ratio_tif.crs, carbon_tif.crs,
                                                                   carbon_tif.width, carbon_tif.height,
                                                                   *carbon_tif.bounds)
            carbon_transform = carbon_tif.transform
            carbon_crs = carbon_tif.crs

            # Reproject the C/N ratio raster to match the carbon map
            cn_ratio_resampled = np.zeros((height, width), dtype=cn_ratio_meta['dtype'])
            reproject(
                source=cn_ratio_data,
                destination=cn_ratio_resampled,
                src_transform=cn_transform,
                src_crs=cn_crs,
                dst_transform=carbon_transform,
                dst_crs=carbon_crs,
                resampling=Resampling.nearest
            )
            # Multiply carbon by the inverse of C/N ratio
            nitrogen_data = np.where(cn_ratio_resampled > 0, carbon_data / cn_ratio_resampled, 0)

            # Use the metadata from the carbon raster
            nitrogen_profile = carbon_tif.profile
            nitrogen_profile.update(dtype=rasterio.float32, count=1, compress='lzw')

            # Save nitrogen raster
            with rasterio.open(n_map, 'w', **nitrogen_profile) as dst:
                dst.write(nitrogen_data, 1)

print("Nitrogen rasters have been created successfully.")

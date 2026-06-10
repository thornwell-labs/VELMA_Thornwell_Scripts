"""
Creates a map of soil type ID's based on the clustered restrictive depth types and the C/N ratios
"""

import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np

# Define desired file paths
resdepth_tif = 'path/to/SOLUS/clustered_resdepth_Puget_Sound.tif'
cn_ratio_tif = 'path/to/SOLUS/cn_ratio.tif'
output_tif = 'path/to/SOLUS/soil_types_map.tif'


# ----- Shouldn't need to edit anything below this line -----

# Load the resdepth raster
with rasterio.open(resdepth_tif) as resdepth_src:
    # Read resdepth data and metadata
    resdepth_data = resdepth_src.read(1)
    resdepth_meta = resdepth_src.meta
    resdepth_bounds = resdepth_src.bounds

    # Open the cn_ratio raster to reproject and clip
    with rasterio.open(cn_ratio_tif) as cn_src:
        # Calculate the transform and metadata to match resdepth
        transform, width, height = calculate_default_transform(
            cn_src.crs, resdepth_src.crs,
            resdepth_src.width, resdepth_src.height,
            *resdepth_bounds
        )

        cn_meta = cn_src.meta.copy()
        cn_meta.update({
            'crs': resdepth_src.crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        # Reproject and clip cn_ratio data to match resdepth
        cn_data = np.zeros((height, width), dtype=cn_meta['dtype'])

        reproject(
            source=rasterio.band(cn_src, 1),
            destination=cn_data,
            src_transform=cn_src.transform,
            src_crs=cn_src.crs,
            dst_transform=transform,
            dst_crs=resdepth_src.crs,
            resampling=Resampling.nearest
        )

    # Create the soil type by concatenating values (e.g., 212 for resdepth=2, cn_ratio=12)
    soil_types_data = resdepth_data * 100 + cn_data

    # Update metadata to save the new raster
    output_meta = resdepth_meta.copy()
    output_meta.update(count=1)

    # Save the output
    with rasterio.open(output_tif, 'w', **output_meta) as output_raster:
        output_raster.write(soil_types_data, 1)

print("Soil types map created and saved as", output_tif)

"""
Masks an interpolated soil organic carbon raster to a single restrictive-depth
cluster. Builds a mask from the clustered restrictive depth raster (one k-means
group), then keeps SOC values only where the mask applies, writing both the
mask and the clipped SOC raster.
"""

import rasterio
import numpy as np

# Define file paths
raster_trim_path = 'path/to/SOLUS/clustered_resdepth_Puget_Sound_clipped.tif'
raster_keep_path = 'path/to/SOLUS/SOC/shallow/interpolated_soc_5.875.tif'
mask_output_path = 'path/to/SOLUS/SOC/shallow/shallow_resdepth.tif'
resdepth_group = 2  # Which k-means group are you trying to create a mask for?
final_output_path = 'path/to/SOLUS/SOC/shallow/interpolated_soc_5.875_clipped.tif'

# Define the NoData value
nodata_value = -9999

# Step 1: Create mask raster (1 for valid cells, -9999 for NoData)
with rasterio.open(raster_trim_path) as src_trim:
    trim_array = src_trim.read(1)
    mask_meta = src_trim.meta.copy()

    # Create the mask: 1 where raster_trim == 0, else NoData (-9999)
    mask_array = np.where(trim_array == resdepth_group, 1, nodata_value)

    # Update metadata to set NoData value
    mask_meta.update(dtype=rasterio.float32, nodata=nodata_value)

    # Write the mask raster to disk
    with rasterio.open(mask_output_path, 'w', **mask_meta) as dst_mask:
        dst_mask.write(mask_array, 1)

# Step 2: Apply the mask to the interpolated restrictive depth raster
with rasterio.open(raster_keep_path) as src_keep, rasterio.open(mask_output_path) as src_mask:
    keep_array = src_keep.read(1)
    mask_array = src_mask.read(1)
    final_meta = src_keep.meta.copy()

    # Apply the mask: keep raster_keep where mask == 1, else set to NoData
    final_array = np.where(mask_array == 1, keep_array, nodata_value)

    # Update metadata to set NoData value
    final_meta.update(dtype=rasterio.float32, nodata=nodata_value)

    # Write the final raster to disk
    with rasterio.open(final_output_path, 'w', **final_meta) as dst_final:
        dst_final.write(final_array, 1)

print("Masking and raster trimming completed.")

"""
Accepts two chemistry pool folders and a land cover file
Calculates mean percent difference in each chemistry pool by land cover type
"""

import os
import rasterio
import numpy as np
import pandas as pd


old_spatial_pools = 'path/to/VELMA_Watersheds/Huge/Data_Inputs30m/o_10_ChemistryPools/1990_Mar2025'
new_spatial_pools = 'path/to/VELMA_Watersheds/Huge/Data_Inputs30m/o_10_ChemistryPools/EndState_2000'
land_cover_file = 'path/to/VELMA_Watersheds/Huge/Data_Inputs30m/m_5_Coverage/Huge30m_LandCover19.asc'
out_file = 'path/to/VELMA_Watersheds/Huge/Analysis/Spatial Pool Comparison/mean_percent_diff_by_landcover.csv'

# Load land cover data
with rasterio.open(land_cover_file) as src:
    lc_data = src.read(1)
    lc_nodata = src.nodata

# Get list of unique land cover values, excluding zero and NaN, and start the dataframe
unique_lc = np.unique(lc_data)
unique_lc = unique_lc[(unique_lc != lc_nodata) & (unique_lc!=0)]
df = pd.DataFrame({"LandCover": unique_lc})

for root, dirs, files in os.walk(new_spatial_pools):
    for filename in files:
        pool_name = filename.removesuffix('.asc')
        filepath = os.path.join(new_spatial_pools, filename)
        with rasterio.open(filepath) as src:
            new_data = src.read(1).astype(float)
            new_nodata = src.nodata
        filepath = os.path.join(old_spatial_pools, filename)
        with rasterio.open(filepath) as src:
            old_data = src.read(1).astype(float)
            old_nodata = src.nodata
        
        # Create mask to filter no data values and avoid dividing by zero
        mask = (
        (lc_data != lc_nodata) & (lc_data != 0) &
        (old_data != old_nodata) & (new_data != new_nodata) &
        (~np.isnan(old_data)) & (~np.isnan(new_data))
        )
        valid = mask & (old_data != 0) & (new_data != 0)
        
        # Calculate mean percent difference by land cover
        percent_diff_data = np.full_like(old_data, np.nan, dtype=float)
        percent_diff_data[valid] = (new_data[valid] - old_data[valid]) / old_data[valid] * 100.0
        
        # --- Calculate mean percent difference by land cover ---
        col_values = []
        for lc in unique_lc:
            lc_mask = (lc_data == lc) & valid
            if np.any(lc_mask):
                mean_diff = np.nanmean(percent_diff_data[lc_mask])
            else:
                mean_diff = np.nan
            col_values.append(mean_diff)

        # Add column for this pool
        df[pool_name] = col_values

df.to_csv(out_file, index=False)
print(f"Saved combined results to {out_file}")

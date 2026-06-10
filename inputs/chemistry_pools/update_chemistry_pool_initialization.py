"""
Overwrites nitrate, ammonium, biomass, and detritus values in VELMA chemistry
pool initialization rasters by land cover class. For each pool type, reads a
CSV of per-land-cover values and applies them to every cell of the matching
class, writing updated rasters to a new initialization folder. Generalized
version of biomass_initialization_update.py.
"""

import rasterio
import numpy as np
import pandas as pd

land_cover_file_path ='path/to/VELMA_Watersheds/Snohomish/Data_Inputs30m/m_5_Coverage/Snohomish_LandCover19.asc'
chemistry_pool_folder_path = 'path/to/VELMA_Watersheds/Snohomish/Data_Inputs30m/o_10_ChemistryPools/1990_Nov2024/'
output_folder_path = 'path/to/VELMA_Watersheds/Snohomish/Data_Inputs30m/o_10_ChemistryPools/1990_Mar2025/'

data = ['nitrate', 'ammonium', 'biomass', 'detritus']

for item in data:
    init_changes_file_path = f'path/to/VELMA_Watersheds/{item}_initialization_changes.csv'

    changes_df = pd.read_csv(init_changes_file_path, index_col='Land_Cover')

    with rasterio.open(land_cover_file_path) as src:
            land_cover_data = src.read(1)

    for file_name in changes_df.columns:
        with rasterio.open(f'{chemistry_pool_folder_path}{file_name}') as src:
            biomass_data = src.read(1)
            profile = src.profile
        for land_cover_value in changes_df.index:
            mask = land_cover_data == land_cover_value
            biomass_value = changes_df.at[land_cover_value, file_name]
            biomass_data[mask] = biomass_value
        biomass_data = np.round(biomass_data, 6)
        with rasterio.open(f'{output_folder_path}{file_name}', 'w', **profile) as dst:
            dst.write(biomass_data, 1)

        print(f"{file_name} complete. Updated raster saved.")

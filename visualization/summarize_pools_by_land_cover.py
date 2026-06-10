"""
Summarizes VELMA chemistry pool initialization rasters by land cover type.
For each pool file (carbon and nitrogen pools, detritus, humus), computes
per-land-cover-class statistics, comparing 1990 and 2010 end-state pools to
inspect how the spatial pools differ by cover.
"""

import pandas as pd
import numpy as np
import rasterio

chemistry_files = ['agAverageBiomass.asc', 'C_g_AgStem.asc', 'C_g_BgStem.asc', 'C_g_Det_AgStem.asc', 'C_g_Det_BgStem_1.asc', 'C_g_Det_BgStem_2.asc', 
                   'C_g_Det_BgStem_3.asc', 'C_g_Det_BgStem_4.asc', 'C_g_Det_leaf.asc', 'C_g_Det_root_1.asc', 'C_g_Det_root_2.asc', 'C_g_Det_root_3.asc', 
                   'C_g_Det_root_4.asc', 'C_g_Humus_1.asc', 'C_g_Humus_2.asc', 'C_g_Humus_3.asc', 'C_g_Humus_4.asc', 'C_g_leaf.asc', 'C_g_root_1.asc', 
                   'C_g_root_2.asc', 'C_g_root_3.asc', 'C_g_root_4.asc', 'DOC_Pool_1.asc',  'DOC_Pool_2.asc', 'DOC_Pool_3.asc', 'DOC_Pool_4.asc', 'DON_Pool_1.asc', 
                   'DON_Pool_2.asc', 'DON_Pool_3.asc', 'DON_Pool_4.asc', 'NH4_Pool_1.asc', 'NH4_Pool_2.asc', 'NH4_Pool_3.asc', 'NH4_Pool_4.asc', 'NO3_Pool_1.asc', 
                   'NO3_Pool_2.asc', 'NO3_Pool_3.asc', 'NO3_Pool_4.asc', 'N_g_AgStem.asc', 'N_g_BgStem.asc', 'N_g_Det_AgStem.asc', 'N_g_Det_BgStem_1.asc', 
                   'N_g_Det_BgStem_2.asc', 'N_g_Det_BgStem_3.asc', 'N_g_Det_BgStem_4.asc', 'N_g_Det_leaf.asc', 'N_g_Det_root_1.asc', 'N_g_Det_root_2.asc', 
                   'N_g_Det_root_3.asc', 'N_g_Det_root_4.asc', 'N_g_Humus_1.asc', 'N_g_Humus_2.asc', 'N_g_Humus_3.asc', 'N_g_Humus_4.asc', 'N_g_leaf.asc', 
                   'N_g_root_1.asc', 'N_g_root_2.asc', 'N_g_root_3.asc', 'N_g_root_4.asc']


land_cover_dict = {5: 'Alder5Percent', 6: 'Alder17Percent', 7: 'Alder37Percent', 8: 'Alder62Percent', 9: 'Alder88Percent', 11: 'Water', 12: 'SnowIce',
                   21: 'DevelopedOpenSpace', 22: 'DevelopedLowIntensity', 23: 'DevelopedMediumIntensity', 24: 'DevelopedHighIntensity', 31: 'BareLand',
                   42: 'EvergreenForest', 43: 'MixedForest', 52: 'ShrubScrub', 71: 'Grassland', 81: 'Pasture', 82: 'Cultivated', 90: 'Wetlands'}  
                   # All 19 land cover codes with names


lc_file_path = 'path/to/VELMA_Watersheds/Samish/Data_Inputs30m/m_5_Coverage/Samish30m_LandCover19.asc'
chemistry_1990_path = 'path/to/VELMA_Watersheds/Samish/Data_Inputs30m/o_10_ChemistryPools/1990_Nov2024/'
chemistry_2010_path = 'path/to/VELMA_Watersheds/Samish/Data_Inputs30m/o_10_ChemistryPools/2010_Nov2024/'

with rasterio.open(lc_file_path) as lc_src:
    lc_data = lc_src.read(1)

for key, lc_name in land_cover_dict.items():
    mask = (lc_data == key)
    df_1990 = pd.DataFrame({'File': chemistry_files, 'Minimum': np.nan, 'Maximum': np.nan, 'Average': np.nan})
    df_2010 = pd.DataFrame({'File': chemistry_files, 'Minimum': np.nan, 'Maximum': np.nan, 'Average': np.nan})
    
    # Look up all cells with matching code in the land cover file
    for file_name in chemistry_files:
        file_path_1990 = chemistry_1990_path+file_name
        file_path_2010 = chemistry_2010_path+file_name
        
        with rasterio.open(file_path_1990) as chem_1990_src, rasterio.open(file_path_2010) as chem_2010_src:
            chem_data_1990 = chem_1990_src.read(1)  # Read the first band
            chem_data_2010 = chem_2010_src.read(1)
        
        selected_1990 = chem_data_1990[mask]
        selected_2010 = chem_data_2010[mask]
        
        # Compute statistics
        if selected_1990.size > 0:  # Ensure there are cells for this land cover type
            df_1990.loc[df_1990['File'] == file_name, ['Minimum', 'Maximum', 'Average']] = [
                selected_1990.min(), selected_1990.max(), selected_1990.mean()]
        if selected_2010.size > 0:
            df_2010.loc[df_2010['File'] == file_name, ['Minimum', 'Maximum', 'Average']] = [
                selected_2010.min(), selected_2010.max(), selected_2010.mean()]
        
    # Normalize values by area (30m x 30m = 900 m² per cell)
    # df_1990[['Minimum', 'Maximum', 'Average']] /= 900
    # df_2010[['Minimum', 'Maximum', 'Average']] /= 900
    
    # Save results
    df_1990.to_csv(f'path/to/VELMA_Watersheds/Samish/Data_Inputs30m/o_10_ChemistryPools/{lc_name}_1990.csv', index=False)
    df_2010.to_csv(f'path/to/VELMA_Watersheds/Samish/Data_Inputs30m/o_10_ChemistryPools/{lc_name}_2010.csv', index=False)

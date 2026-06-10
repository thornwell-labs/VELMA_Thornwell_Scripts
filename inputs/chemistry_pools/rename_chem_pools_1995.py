"""
Renames VELMA end-state spatial data writer files (e.g.
Spatial_NO3_L#1_1_1995_365.asc) to the chemistry pool file names VELMA expects
as initialization inputs (e.g. NO3_Pool_1.asc). Edit the year embedded in the
dictionary keys to match the end-state being converted.
"""

import os

rename_dict = {
 'Spatial_DOC_L#1_1_1995_365.asc': 'DOC_Pool_1.asc', 
 'Spatial_DOC_L#2_1_1995_365.asc': 'DOC_Pool_2.asc', 
 'Spatial_DOC_L#3_1_1995_365.asc': 'DOC_Pool_3.asc', 
 'Spatial_DOC_L#4_1_1995_365.asc': 'DOC_Pool_4.asc', 
 'Spatial_DON_L#1_1_1995_365.asc': 'DON_Pool_1.asc', 
 'Spatial_DON_L#2_1_1995_365.asc': 'DON_Pool_2.asc', 
 'Spatial_DON_L#3_1_1995_365.asc': 'DON_Pool_3.asc', 
 'Spatial_DON_L#4_1_1995_365.asc': 'DON_Pool_4.asc', 
 'Spatial_NH4_L#1_1_1995_365.asc': 'NH4_Pool_1.asc', 
 'Spatial_NH4_L#2_1_1995_365.asc': 'NH4_Pool_2.asc', 
 'Spatial_NH4_L#3_1_1995_365.asc': 'NH4_Pool_3.asc', 
 'Spatial_NH4_L#4_1_1995_365.asc': 'NH4_Pool_4.asc', 
 'Spatial_NO3_L#1_1_1995_365.asc': 'NO3_Pool_1.asc', 
 'Spatial_NO3_L#2_1_1995_365.asc': 'NO3_Pool_2.asc', 
 'Spatial_NO3_L#3_1_1995_365.asc': 'NO3_Pool_3.asc', 
 'Spatial_NO3_L#4_1_1995_365.asc': 'NO3_Pool_4.asc', 
 'Spatial_BIOMASS_AG_STEM_N_ALL_1_1995_365.asc': 'N_g_AgStem.asc', 
 'Spatial_BIOMASS_BG_STEM_N_ALL_1_1995_365.asc': 'N_g_BgStem.asc', 
 'Spatial_DETRITUS_AG_STEM_N_ALL_1_1995_365.asc': 'N_g_Det_AgStem.asc', 
 'Spatial_DETRITUS_BG_STEM_N_L#1_1_1995_365.asc': 'N_g_Det_BgStem_1.asc', 
 'Spatial_DETRITUS_BG_STEM_N_L#2_1_1995_365.asc': 'N_g_Det_BgStem_2.asc', 
 'Spatial_DETRITUS_BG_STEM_N_L#3_1_1995_365.asc': 'N_g_Det_BgStem_3.asc', 
 'Spatial_DETRITUS_BG_STEM_N_L#4_1_1995_365.asc': 'N_g_Det_BgStem_4.asc', 
 'Spatial_DETRITUS_LEAF_N_ALL_1_1995_365.asc': 'N_g_Det_leaf.asc', 
 'Spatial_DETRITUS_ROOT_N_L#1_1_1995_365.asc': 'N_g_Det_root_1.asc', 
 'Spatial_DETRITUS_ROOT_N_L#2_1_1995_365.asc': 'N_g_Det_root_2.asc', 
 'Spatial_DETRITUS_ROOT_N_L#3_1_1995_365.asc': 'N_g_Det_root_3.asc', 
 'Spatial_DETRITUS_ROOT_N_L#4_1_1995_365.asc': 'N_g_Det_root_4.asc', 
 'Spatial_BIOMASS_LEAF_N_ALL_1_1995_365.asc': 'N_g_leaf.asc', 
 'Spatial_BIOMASS_ROOT_N_L#1_1_1995_365.asc': 'N_g_root_1.asc', 
 'Spatial_BIOMASS_ROOT_N_L#2_1_1995_365.asc': 'N_g_root_2.asc', 
 'Spatial_BIOMASS_ROOT_N_L#3_1_1995_365.asc': 'N_g_root_3.asc', 
 'Spatial_BIOMASS_ROOT_N_L#4_1_1995_365.asc': 'N_g_root_4.asc',
 'Spatial_HUMUS_L#1_1_1995_365.asc': 'N_g_Humus_1.asc',
 'Spatial_HUMUS_L#2_1_1995_365.asc': 'N_g_Humus_2.asc',
 'Spatial_HUMUS_L#3_1_1995_365.asc': 'N_g_Humus_3.asc',
 'Spatial_HUMUS_L#4_1_1995_365.asc': 'N_g_Humus_4.asc'
 }

target_dir = r'path/to/VELMA_Watersheds/Huge/Data_Inputs30m/o_10_ChemistryPools/EndState_1995'

for root, dirs, files in os.walk(target_dir):
    for file in files:
        if file in rename_dict:
            old_path = os.path.join(root, file)
            new_path = os.path.join(root, rename_dict[file])
            os.rename(old_path, new_path)
            
"""
Calculates yearly watershed-average humus nitrogen (gN/m^2) from VELMA spatial
humus data writers for multiple nitrogen-source-elimination scenarios, along
with the year-over-year change in humus. Part of the Samish nitrogen source
attribution analysis.
"""

import numpy as np
import os
import pandas as pd

# Specify results folders and C/N ratio information (use raster_reprojection.py to generate C/N ratio file)
analysis_folder_path = 'path/to/VELMA_Watersheds/Samish/Analysis/Nitrogen_Sources'

scenario_dict = {
    'Samish Original': 'path/to/VELMA_Watersheds/Samish/Results/WA_Samish30m_Historical_resampled_3',
    'No Deposition': 'path/to/VELMA_Watersheds/Samish/Results/WA_Samish30m_Eliminate_Deposition_resampled_3',
    'No Alder Nitrogen Fixation': 'path/to/VELMA_Watersheds/Samish/Results/WA_Samish30m_Eliminate_Nitrogen_Fixation_resampled_3',
    'No Fertilization': 'path/to/VELMA_Watersheds/Samish/Results/WA_Samish30m_Eliminate_Fertilization_resampled_3',
    'No Septic': 'path/to/VELMA_Watersheds/Samish/Results/WA_Samish30m_Eliminate_Septic_resampled_3'
}

for name, folder in scenario_dict.items():
    average_delineated_nitrogen = []
    years = []
    for root, dirs, files in os.walk(folder):
        for filename in files:
            if filename.startswith('Spatial_HUMUS'):
                parts = filename.split('_')
                year = int(parts[-2])
                years.append(year)
                humus_path = os.path.join(root, filename)
                humus_data = np.loadtxt(humus_path, skiprows=6)
                nodata_value = -3.4028235e38
                humus_data[humus_data == nodata_value] = 0                    
                humus_data = humus_data[(humus_data != 0) & (~np.isnan(humus_data)) & (~np.isinf(humus_data))]
                average_delineated_nitrogen.append(humus_data.mean())
    df = pd.DataFrame({'Average_Delineated_Humus(gN/m2)': average_delineated_nitrogen}, index=years)
    df['Delta_Humus(gN/m2)'] = df['Average_Delineated_Humus(gN/m2)'].shift(-1) - df['Average_Delineated_Humus(gN/m2)']
    df.to_csv(os.path.join(analysis_folder_path, f'{name}_avg_humus_by_year.csv'))
    
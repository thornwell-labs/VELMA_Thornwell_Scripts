"""
Tracks the yearly nitrogen budget across VELMA nitrogen-source-elimination
scenarios. Computes year-over-year change in NH4/NO3/DON pools and total
annual nitrogen losses from each scenario's DailyResults, supporting the
nitrogen source attribution analysis.
"""

import pandas as pd
import os
import numpy as np

# Define scenarios and where the results should go
out_folder = 'path/to/VELMA_Watersheds/Samish/Analysis/Nitrogen_Sources'
scenario_dict = {
    'Samish Original': 'path/to/VELMA_Watersheds/Samish/Results/WA_Samish30m_Historical_resampled_3/DailyResults.csv',
    'No Deposition': 'path/to/VELMA_Watersheds/Samish/Results/WA_Samish30m_Eliminate_Deposition_resampled_3/DailyResults.csv',
    'No Alder Nitrogen Fixation': 'path/to/VELMA_Watersheds/Samish/Results/WA_Samish30m_Eliminate_Nitrogen_Fixation_resampled_3/DailyResults.csv',
    'No Fertilization': 'path/to/VELMA_Watersheds/Samish/Results/WA_Samish30m_Eliminate_Fertilization_resampled_3/DailyResults.csv',
    'No Septic': 'path/to/VELMA_Watersheds/Samish/Results/WA_Samish30m_Eliminate_Septic_resampled_3/DailyResults.csv'
}

nitrogen_pools = ['NH4_Pool(gN/m2)_Delineated_Average', 'NO3_Pool(gN/m2)_Delineated_Average', 'DON_Pool(gN/m2)_Delineated_Average']
nitrogen_losses = ['NH4_Loss(gN/day/m2)_Delineated_Average', 'NO3_Loss(gN/day/m2)_Delineated_Average', 'DON_Loss(gN/day/m2)_Delineated_Average']


for name, csv_file in scenario_dict.items():
    # Find the change in pool amount for each year
    delta_df = pd.read_csv(csv_file, usecols=['Year', 'Day']+nitrogen_pools)
    delta_df = delta_df[delta_df['Day'] == 1].set_index('Year')
    delta_df['Delta_DON(gN/m2)'] = delta_df['DON_Pool(gN/m2)_Delineated_Average'].shift(-1) - delta_df['DON_Pool(gN/m2)_Delineated_Average'] # Use shift to subtract from the next row
    delta_df['Delta_NH4(gN/m2)'] = delta_df['NH4_Pool(gN/m2)_Delineated_Average'].shift(-1) - delta_df['NH4_Pool(gN/m2)_Delineated_Average']
    delta_df['Delta_NO3(gN/m2)'] = delta_df['NO3_Pool(gN/m2)_Delineated_Average'].shift(-1) - delta_df['NO3_Pool(gN/m2)_Delineated_Average']
    delta_df = delta_df.drop(columns=['Day']+nitrogen_pools)
    
    # Calculate the total losses over the year
    loss_df = pd.read_csv(csv_file, usecols=['Year', 'Day']+nitrogen_losses)
    loss_df = loss_df.groupby('Year')[nitrogen_losses].sum()
    
    # Calculate average delineated humus nitrogen using spatial data writers
    average_delineated_nitrogen = []
    years = []
    folder = csv_file.removesuffix("/DailyResults.csv")
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
    humus_df = pd.DataFrame({'Average_Delineated_Humus(gN/m2)': average_delineated_nitrogen}, index=years)
    humus_df['Delta_Humus(gN/m2)'] = humus_df['Average_Delineated_Humus(gN/m2)'].shift(-1) - humus_df['Average_Delineated_Humus(gN/m2)']
    humus_df = humus_df.drop(columns=['Average_Delineated_Humus(gN/m2)'])
    
    
    df = loss_df.join(delta_df)
    df = df.join(humus_df)
    df['Yearly_Nitrogen_Change(g/m2)'] = df['Delta_DON(gN/m2)'] + df['Delta_NH4(gN/m2)'] + df['Delta_NO3(gN/m2)'] + df['Delta_Humus(gN/m2)'] - \
        df['NH4_Loss(gN/day/m2)_Delineated_Average'] - df['NO3_Loss(gN/day/m2)_Delineated_Average'] - df['DON_Loss(gN/day/m2)_Delineated_Average']
    df.columns = [col.replace('day', 'year') for col in df.columns]
    df.to_csv(os.path.join(out_folder, f'{name}_yearly_nitrogen_change.csv'))
    
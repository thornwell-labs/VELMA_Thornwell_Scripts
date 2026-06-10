"""
Converts VELMA outlet results into the CSV format required by the Salish Sea
Model (SSM) team. Merges DailyResults.csv nitrogen/runoff columns with water
surface temperature from a cell data writer file, converts units using the
watershed area, and writes a combined daily time series.
"""

import pandas as pd
import numpy as np

# User must specify these file paths, outlet ID, and cell area (in m2)
results_folder = r'path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_StatusQuo_archive\Results_635473'
daily_results_file = f'{results_folder}/DailyResults.csv'
cell_dwriter_file = f'{results_folder}/Cell_i635473_x465_y656_dlnWriter.csv'
output_file = f'{results_folder}/Samish_Status_Quo_Archive_Outlet_SSM_Results.csv'
outlet_id = 635473
cell_area = 30*30

# Shouldn't need to edit anything below this line
# ---------------------------------------------------------------------------

# Specify columns and read in data
daily_results_columns = ['Year', 'Day', 'Runoff_All(mm/day)_Delineated_Average', 'NH4_Loss(gN/day/m2)_Delineated_Average', 
                         'NO3_Loss(gN/day/m2)_Delineated_Average', 'DON_Loss(gN/day/m2)_Delineated_Average', 
                         'DOC_Loss(gC/day/m2)_Delineated_Average']
cell_dwriter_columns = ['Year', 'Jday', 'Water_Surface_Temperature(degrees_C)']

daily_df = pd.read_csv(daily_results_file, usecols=daily_results_columns)
cell_dwriter_df = pd.read_csv(cell_dwriter_file, usecols=cell_dwriter_columns)

# Find watershed area
watershed_area_df = pd.read_csv(f'{results_folder}/ReachSummary.csv', usecols=['iOutlet', 'Reach_plus_Contributor_Cells'], dtype=int)
matches = watershed_area_df.loc[watershed_area_df['iOutlet'] == outlet_id, 'Reach_plus_Contributor_Cells']
if matches.empty:
    raise ValueError(f"Outlet ID {outlet_id} not found in ReachSummary.csv")
elif len(matches) > 1:
    raise ValueError(f"Multiple entries for Reach_ID {outlet_id} found in ReachSummary.csv")
cell_count = matches.values[0]
watershed_area_m2 = cell_area * cell_count

# Create datetime columns
daily_df['Date'] = pd.to_datetime(daily_df['Year'] * 1000 + daily_df['Day'], format='%Y%j')
cell_dwriter_df['Date'] = pd.to_datetime(cell_dwriter_df['Year'] * 1000 + cell_dwriter_df['Jday'], format='%Y%j')
daily_df.drop(columns=['Year', 'Day'], inplace=True)
cell_dwriter_df.drop(columns=['Year', 'Jday'], inplace=True)

# Merge on the Date column
merged_df = pd.merge(daily_df, cell_dwriter_df, on='Date', how='inner')

# Perform unit conversions, protecting against division by zero
# mg/L = 1000 * (gN/day/m2) / (mm/day)
runoff_col = 'Runoff_All(mm/day)_Delineated_Average'

merged_df['NH4_Loss(mg/L)'] = np.where(
    merged_df[runoff_col] > 0,
    1000 * merged_df['NH4_Loss(gN/day/m2)_Delineated_Average'] / merged_df[runoff_col],
    np.nan
)

merged_df['NO3_Loss(mg/L)'] = np.where(
    merged_df[runoff_col] > 0,
    1000 * merged_df['NO3_Loss(gN/day/m2)_Delineated_Average'] / merged_df[runoff_col],
    np.nan
)

merged_df['DON_Loss(mg/L)'] = np.where(
    merged_df[runoff_col] > 0,
    1000 * merged_df['DON_Loss(gN/day/m2)_Delineated_Average'] / merged_df[runoff_col],
    np.nan
)

merged_df['DOC_Loss(mg/L)'] = np.where(
    merged_df[runoff_col] > 0,
    1000 * merged_df['DOC_Loss(gC/day/m2)_Delineated_Average'] / merged_df[runoff_col],
    np.nan
)

# Convert runoff from mm/day to m³/s
# Formula: runoff_mm_per_day * watershed_area_m2 / 1000 / 86400
merged_df['Runoff(m3/s)'] = (merged_df[runoff_col] * watershed_area_m2) / (1000 * 86400)

# Drop original unit columns
merged_df.drop(columns=[
    'Runoff_All(mm/day)_Delineated_Average',
    'NH4_Loss(gN/day/m2)_Delineated_Average',
    'NO3_Loss(gN/day/m2)_Delineated_Average',
    'DON_Loss(gN/day/m2)_Delineated_Average',
    'DOC_Loss(gC/day/m2)_Delineated_Average'
], inplace=True)

# Save
merged_df.to_csv(output_file, index=False)

print(f"Saved merged results to {output_file}")

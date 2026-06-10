"""
Calculates yearly Nash-Sutcliffe Efficiency (NSE) between two VELMA result
files — e.g. a full-resolution run versus a resampled run — treating the first
as 'observed'. Useful for quantifying how much a downscaled grid degrades the
simulation. See nse_calculator_obs.py to compare against real observations.
"""

import numpy as np
import pandas as pd

file_path1 = r'path\to\VELMA_Watersheds\Nisqually\Results\MULTI_WA_Nisqually30m_28Feb2025_Hyak\Results_1448149\DailyResults.csv'
file_path2 = r'path\to\VELMA_Watersheds\Nisqually\Results\MULTI_WA_Nisqually30m_28Feb2025_resampled_14\Results_7363\DailyResults.csv'
data_column = 'Runoff_All(mm/day)_Delineated_Average'
columns = ['Year', 'Day', data_column]

# Read CSV files
df1 = pd.read_csv(file_path1, usecols=columns)
df2 = pd.read_csv(file_path2, usecols=columns)

# Convert Year and Day to datetime and set as index
df1['Date'] = pd.to_datetime(df1['Year'].astype(str) + df1['Day'].astype(str), format='%Y%j')
df2['Date'] = pd.to_datetime(df2['Year'].astype(str) + df2['Day'].astype(str), format='%Y%j')

df1.set_index('Date', inplace=True)
df2.set_index('Date', inplace=True)

# Ensure both dataframes are aligned and return data grouped by year
def align_group_data(observed_df, simulated_df):
    aligned = pd.concat([observed_df[[data_column]], simulated_df[[data_column]]], axis=1, keys=['Observed', 'Simulated'])
    aligned.columns = ['Observed', 'Simulated']
    aligned = aligned.dropna()  # Remove NaN values
    grouped = aligned.groupby(aligned.index.year)
    return grouped

# Calculate NSE for each year
def calculate_nse(grouped_data):
    nse_by_year = {}
    for year, data in grouped_data:
        try:
            obs = pd.to_numeric(data['Observed'], errors='coerce')
            sim = pd.to_numeric(data['Simulated'], errors='coerce')

            if obs.isna().all() or sim.isna().all():
                continue  # Skip if there are no valid data points
            
            nse = 1 - (np.sum((obs - sim) ** 2) / np.sum((obs - np.mean(obs)) ** 2))
            nse_by_year[year] = nse
        except Exception as e:
            print(f"Error processing year {year}: {e}")
    return nse_by_year

# Process data
grouped_data = align_group_data(df1, df2)
nse_by_year = calculate_nse(grouped_data)

# Print results
nse_list = []
for year, nse in nse_by_year.items():
    print(f'{year},{np.round(nse, 3)}')
    nse_list.append(nse)

if nse_list:
    print(f'Average NSE is {np.round(np.average(nse_list), 3)}')
else:
    print('No valid NSE values calculated.')

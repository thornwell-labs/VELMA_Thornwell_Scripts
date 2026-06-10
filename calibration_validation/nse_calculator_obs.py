"""
Calculates yearly Nash-Sutcliffe Efficiency (NSE) between a VELMA-simulated
variable and a VELMA-format observed data file (e.g. USGS streamflow),
aligning the daily series by date and reporting NSE for each year.
"""

import numpy as np
import pandas as pd

sim_file = 'path/to/VELMA_Watersheds/Snohomish/Results/WA_Snohomish_30m_April18thDelivery_resampled_3/DailyResults_to2014.csv'
obs_file = 'path/to/VELMA_Watersheds/Snohomish/Data_Inputs30m/m_7_Observed/USGS12131500_Snohomish_1981-2025.csv'
start_obs_year = 1981
data_column = 'Runoff_All(mm/day)_Delineated_Average'
sim_columns = ['Year', 'Day', data_column]

# Read CSV files
sim_df = pd.read_csv(sim_file, usecols=sim_columns)
obs_df = pd.read_csv(obs_file, header=None, usecols=[0])
obs_df.columns = [data_column]

# Convert Year and Day to datetime and set as index
sim_df['Date'] = pd.to_datetime(sim_df['Year'].astype(str) + sim_df['Day'].astype(str), format='%Y%j')
obs_df['Date'] = pd.date_range(start=f'{start_obs_year}-01-01', periods=len(obs_df), freq='D')

sim_df.set_index('Date', inplace=True)
obs_df.set_index('Date', inplace=True)

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
grouped_data = align_group_data(obs_df, sim_df)
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

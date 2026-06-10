"""
Calculates seasonal Nash-Sutcliffe Efficiency (NSE) between a VELMA-simulated
variable and a VELMA-format observed data file, reporting NSE by season and
year to a CSV.
"""

import numpy as np
import pandas as pd

obs_file = 'path/to/VELMA_Watersheds/Duckabush/Data_Inputs30m/m_7_Observed/USGS1205400_Duckabush_streamflow_1981-2021.csv'
sim_file = 'path/to/VELMA_Watersheds/Duckabush/Results/MULTI_WA_Duckabush30m_8Apr2025_Hyak/Results_150181/DailyResults.csv'
out_path = 'path/to/VELMA_Watersheds/Duckabush/Results/MULTI_WA_Duckabush30m_8Apr2025_Hyak/Results_150181/seasonal_nse.csv'
start_obs_year = 1981
data_column = 'Runoff_All(mm/day)_Delineated_Average'
# 'NH4_Loss(gN/day/m2)_Delineated_Average', 'NO3_Loss(gN/day/m2)_Delineated_Average', 'DOC_Loss(gC/day/m2)_Delineated_Average', 'Runoff_All(mm/day)_Delineated_Average'
# 'Water_Surface_Temperature(degrees_C)'

if 'DailyResults' in sim_file:
    day_key = 'Day'
elif 'dlnWriter' in sim_file:
    day_key = 'Jday'

sim_columns = ['Year', day_key, data_column]

# Read CSV files
sim_df = pd.read_csv(sim_file, usecols=sim_columns)
obs_df = pd.read_csv(obs_file, header=None, usecols=[0])
obs_df.columns = [data_column]

# Convert Year and Day to datetime and set as index
obs_df['Date'] = pd.date_range(start=f'{start_obs_year}-01-01', periods=len(obs_df), freq='D')
sim_df['Date'] = pd.to_datetime(sim_df['Year'].astype(str) + sim_df[day_key].astype(str), format='%Y%j')

obs_df.set_index('Date', inplace=True)
sim_df.set_index('Date', inplace=True)

# Ensure both dataframes are aligned and return data grouped by year
def align_group_data(observed_df, simulated_df):
    aligned = pd.concat([observed_df[[data_column]], simulated_df[[data_column]]], axis=1, keys=['Observed', 'Simulated'])
    aligned.columns = ['Observed', 'Simulated']
    aligned = aligned.dropna()  # Remove NaN values
    grouped = aligned.groupby(aligned.index.year)
    return grouped

season_dict = {
    '1': range(91, 181+1),  # Spring: April - June
    '2': range(182, 273+1),  # Summer: July - September
    '3': range(274, 365+1),  # Fall: October - December
    '4': range(1, 90+1)  # Winter: January - March
}

# Calculate NSE for each season in each year
def calculate_nse(grouped_data):
    nse_by_year = {}
    for year, data in grouped_data:
        nse_list = []
        for days in season_dict.values():
            try:
                season_data = data[data.index.dayofyear.isin(days)]
                obs = pd.to_numeric(season_data['Observed'], errors='coerce')
                sim = pd.to_numeric(season_data['Simulated'], errors='coerce')

                if obs.isna().all() or sim.isna().all():
                    continue  # Skip if there are no valid data points
                
                nse = 1 - (np.sum((obs - sim) ** 2) / np.sum((obs - np.mean(obs)) ** 2))
                nse_list.append(nse)
            except Exception as e:
                print(f"Error processing year {year}: {e}")
        nse_by_year[year] = nse_list
    return nse_by_year

# Process data
grouped_data = align_group_data(obs_df, sim_df)
nse_by_year = calculate_nse(grouped_data)

nse_df = pd.DataFrame(nse_by_year)
nse_df.to_csv(out_path, index=False)

# Print results
nse_list = []
for year, nse in nse_by_year.items():
    print(f'{year},{np.round(nse, 3)}')
    nse_list.append(nse)

if nse_list:
    print(f'Average NSE is {np.round(np.average(nse_list), 3)}')
else:
    print('No valid NSE values calculated.')

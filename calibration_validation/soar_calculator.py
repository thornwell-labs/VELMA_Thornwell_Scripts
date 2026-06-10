"""
Calculates the simulated-to-observed runoff ratio (SOAR) by year, both annual
and summer-only, between a VELMA run and observed USGS streamflow, aligning
the daily series by date.
"""

import numpy as np
import pandas as pd

obs_file = r"path\to\VELMA_Watersheds\Stillaguamish\Data_Inputs30m\m_7_Observed\USGS12167000_Stillaguamish_nearArlington_streamflow_1987-2021.csv"
sim_file = r"path\to\VELMA_Watersheds\Stillaguamish\Results\MULTI_WA_Stillaguamish30m_30Jun2025_Hyak\Results_2100476\DailyResults.csv"
start_obs_year = 1987
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

# Calculate SOAR and summertime SOAR for each year
def calculate_soar(grouped_data):
    soar_by_year = {}
    summer_soar_by_year = {}
    for year, data in grouped_data:
        try:
            obs = pd.to_numeric(data['Observed'], errors='coerce')
            sim = pd.to_numeric(data['Simulated'], errors='coerce')

            if obs.isna().all() or sim.isna().all():
                continue  # Skip if there are no valid data points
            
            obs_sum = np.sum(obs)
            sim_sum = np.sum(sim)
            soar_by_year[year] = sim_sum / obs_sum
            
            obs = pd.to_numeric(data['Observed'], errors='coerce')[data.index.month.isin([7, 8, 9])]  # Extra filter for July through September
            sim = pd.to_numeric(data['Observed'], errors='coerce')[data.index.month.isin([7, 8, 9])]
            
            if obs.isna().all() or sim.isna().all():
                continue  # Skip if there are no valid data points
            
            obs_sum = np.sum(obs)
            sim_sum = np.sum(sim)
            summer_soar_by_year[year] = sim_sum / obs_sum

        except Exception as e:
            print(f"Error processing year {year}: {e}")
    return soar_by_year, summer_soar_by_year

# Process data
grouped_data = align_group_data(obs_df, sim_df)
soar_by_year, summer_soar_by_year = calculate_soar(grouped_data)

# Print results
soar_list = []
for year, soar in soar_by_year.items():
    # print(f'{year},{np.round(soar,3)}')
    soar_list.append(soar)

if soar_list:
    print(f'Average overall SOAR is {np.round(np.average(soar_list),3)}')
else:
    print('No valid SOAR values calculated.')

summer_soar_list = []
for year, summer_soar in summer_soar_by_year.items():
    # print(f'{year},{np.round(summer_soar,3)}')
    summer_soar_list.append(soar)

if summer_soar_list:
    print(f'Average overall summertime SOAR is {np.round(np.average(summer_soar_list),3)}')
else:
    print('No valid summertime SOAR values calculated.')

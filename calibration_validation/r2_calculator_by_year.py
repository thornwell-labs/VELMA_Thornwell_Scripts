"""
Calculates the yearly coefficient of determination (R^2) between a
VELMA-simulated variable and a VELMA-format observed data file, aligning the
daily series by date and reporting R^2 for each year.
"""

import numpy as np
import pandas as pd

sim_file = 'path/to/VELMA_Watersheds/Stillaguamish/Results/MULTI_WA_Stillaguamish30m_3Apr2025_Hyak/Results_2016253/DailyResults.csv'
obs_file = 'path/to/VELMA_Watersheds/Stillaguamish/Data_Inputs30m/m_7_Observed/Ecology_05B110_Stillaguamish_Ammonia_1987-2021.csv'
start_obs_year = 1987
data_column = 'NH4_Loss(gN/day/m2)_Delineated_Average'
# 'NH4_Loss(gN/day/m2)_Delineated_Average', 'NO3_Loss(gN/day/m2)_Delineated_Average', 'DOC_Loss(gC/day/m2)_Delineated_Average', 'Runoff_All(mm/day)_Delineated_Average'
# 'Water_Surface_Temperature(degrees_C)'

if 'DailyResults' in sim_file:
    day_column = 'Day'
else:
    day_column = 'Jday'
sim_columns = ['Year', day_column, data_column]

# Read CSV files
sim_df = pd.read_csv(sim_file, usecols=sim_columns)
obs_df = pd.read_csv(obs_file, header=None, usecols=[0])
obs_df.columns = [data_column]

# Convert Year and Day to datetime and set as index
sim_df['Date'] = pd.to_datetime(sim_df['Year'].astype(str) + sim_df[day_column].astype(str), format='%Y%j')
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

# Calculate R² for each year
def calculate_r2(grouped_data):
    r2_by_year = {}
    number_records = 0
    for year, data in grouped_data:
        try:
            obs = pd.to_numeric(data['Observed'], errors='coerce')
            sim = pd.to_numeric(data['Simulated'], errors='coerce')

            if obs.isna().all() or sim.isna().all():
                continue  # Skip if there are no valid data points
            
            r2 = np.corrcoef(obs, sim)[0, 1] ** 2  # Pearson correlation squared
            r2_by_year[year] = r2
            number_records += len(data)
        except Exception as e:
            print(f"Error processing year {year}: {e}")
    return r2_by_year, number_records

# Process data
grouped_data = align_group_data(obs_df, sim_df)
r2_by_year, number_records = calculate_r2(grouped_data)

# Print results
r2_list = []
for year, r2 in r2_by_year.items():
    print(f'{year},{np.round(r2,3)}')
    if pd.notna(r2):
        r2_list.append(r2)

if r2_list:
    print(f'Average R^2 is {np.round(np.average(r2_list),3)} using {number_records} total data points')
else:
    print('No valid R^2 values calculated.')

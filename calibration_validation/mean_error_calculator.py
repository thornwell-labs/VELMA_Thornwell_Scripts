"""
Calculates the mean error (simulated minus observed) between a VELMA-simulated
variable and a VELMA-format observed data file, converting the per-area result
to kg/day using the watershed area.
"""

import numpy as np
import pandas as pd

obs_file = 'path/to/VELMA_Watersheds/Samish/Data_Inputs30m/m_7_Observed/Ecology_03B050_Samish_Dissolved_Organic_Carbon_1989-2021.csv'
sim_file = 'path/to/VELMA_Watersheds/Samish/Results/MULTI_WA_Samish30m_30Jun2025_Hyak/Results_635473/DailyResults.csv'
start_obs_year = 1989
data_column = 'DOC_Loss(gC/day/m2)_Delineated_Average'
watershed_area = 244933*30*30
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
aligned = pd.concat([obs_df[[data_column]].rename(columns={data_column: 'Observed'}), sim_df[[data_column]].rename(columns={data_column: 'Simulated'})], axis=1)
obs_data = pd.to_numeric(aligned['Observed'], errors='coerce')
sim_data = pd.to_numeric(aligned['Simulated'], errors='coerce')
valid = pd.concat([obs_data, sim_data], axis=1).dropna()
mean_diff = np.average(valid['Simulated'] - valid['Observed'])
mean_diff_kg_day = mean_diff * watershed_area / 1000

print(f'Overall mean difference is {round(mean_diff_kg_day,1)} kg/day based on {len(valid)} data points.')

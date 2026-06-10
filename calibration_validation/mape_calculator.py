"""
Calculates the mean absolute percentage error (MAPE) between a VELMA-simulated
variable and a VELMA-format observed data file, aligning the daily series by
date and ignoring missing observations.
"""

import numpy as np
import pandas as pd

obs_file = 'path/to/VELMA_Watersheds/Skokomish/Data_Inputs30m/m_7_Observed/Ecology_16A070_Skokomish_Ammonia_1987-2021.csv'
sim_file = 'path/to/VELMA_Watersheds/Skokomish/Results/MULTI_WA_Skokomish30m_11Apr2025_Hyak/Results_1365037/DailyResults.csv'
start_obs_year = 1987
data_column = 'NH4_Loss(gN/day/m2)_Delineated_Average'
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
mape = np.abs(np.average((valid['Observed'] - valid['Simulated'])/valid['Observed']))*100

print(f'Overall MAPE is {round(mape,1)}% based on {len(valid)} data points.')

"""
Calculates overall Nash-Sutcliffe Efficiency (NSE) between a VELMA-simulated
variable (runoff, nitrogen loss, DOC, or temperature) and a VELMA-format
observed data file, aligning the daily series by date. See
nse_calculator_by_year.py for a per-year breakdown.
"""

import numpy as np
import pandas as pd

obs_file = r"path\to\VELMA_Watersheds\Duckabush\Data_Inputs30m\m_7_Observed\USGS1205400_Duckabush_streamflow_1987-2021.csv"
sim_file = r"path\to\VELMA_Watersheds\Duckabush\Results\MULTI_WA_Duckabush30m_9Jul2025_Hyak\Results_150181\DailyResults.csv"
start_obs_year = 1987
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

# Ensure both dataframes are aligned and calculate NSE
aligned = pd.concat([obs_df[[data_column]].rename(columns={data_column: 'Observed'}), sim_df[[data_column]].rename(columns={data_column: 'Simulated'})], axis=1)
obs_data = pd.to_numeric(aligned['Observed'], errors='coerce')
sim_data = pd.to_numeric(aligned['Simulated'], errors='coerce')
valid = pd.concat([obs_data, sim_data], axis=1).dropna()
nse = 1 - (np.sum((valid['Observed'] - valid['Simulated']) ** 2) / np.sum((valid['Observed'] - np.mean(valid['Observed'])) ** 2))

print(f'Overall NSE is {round(nse,3)} based on {len(valid)} data points.')

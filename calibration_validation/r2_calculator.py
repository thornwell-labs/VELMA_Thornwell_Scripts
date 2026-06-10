"""
Calculates the overall coefficient of determination (R^2) between a
VELMA-simulated variable and a VELMA-format observed data file, aligning the
daily series by date. See r2_calculator_by_year.py for a per-year breakdown.
"""

import numpy as np
import pandas as pd

obs_file = "path/to/VELMA_Watersheds/Stillaguamish/Data_Inputs30m/m_7_Observed/Ecology_05B110_Stillaguamish_Temperature,_water_1987-2021.csv"
sim_file = "path/to/VELMA_Watersheds/Stillaguamish/Results/MULTI_WA_Stillaguamish30m_16Jul2025_resampled_3_Hyak/Results_220508/Cell_i220508_x604_y256_dlnWriter.csv"
start_obs_year = 1987
data_column = 'Water_Surface_Temperature(degrees_C)'
# 'NH4_Loss(gN/day/m2)_Delineated_Average', 'NO3_Loss(gN/day/m2)_Delineated_Average', 'DOC_Loss(gC/day/m2)_Delineated_Average', 'Runoff_All(mm/day)_Delineated_Average'
# 'Water_Surface_Temperature(degrees_C)'

if 'DailyResults' in sim_file:
    day_column = 'Day'
else:
    day_column = 'Jday'
sim_columns = ['Year', day_column, data_column]

# Load simulation and observed data
sim_df = pd.read_csv(sim_file, usecols=sim_columns)
obs_df = pd.read_csv(obs_file, header=None, usecols=[0])
obs_df.columns = [data_column]

# Set dates
sim_df['Date'] = pd.to_datetime(sim_df['Year'].astype(str) + sim_df[day_column].astype(str), format='%Y%j')
obs_df['Date'] = pd.date_range(start=f'{start_obs_year}-01-01', periods=len(obs_df), freq='D')

# Index by date
sim_df.set_index('Date', inplace=True)
obs_df.set_index('Date', inplace=True)

# Align observed and simulated data
aligned = pd.concat([obs_df[[data_column]], sim_df[[data_column]]], axis=1)
aligned.columns = ['Observed', 'Simulated']

# Convert both columns to numeric and drop any resulting NaNs
aligned['Observed'] = pd.to_numeric(aligned['Observed'], errors='coerce')
aligned['Simulated'] = pd.to_numeric(aligned['Simulated'], errors='coerce')
aligned = aligned.dropna()

# Compute R² if possible
if not aligned.empty:
    r2 = np.corrcoef(aligned['Observed'], aligned['Simulated'])[0, 1] ** 2
    print(f'R² for {len(aligned)} total data points is {np.round(r2, 3)}')
else:
    print('No valid data available to calculate R².')
    
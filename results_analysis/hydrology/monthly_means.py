"""
Calculates and plots monthly mean flows for observed versus VELMA-simulated
runoff over a chosen year range, converting both series from mm to cfs using
the watershed area.
"""

import pandas as pd
import matplotlib.pyplot as plt
import statistics
from datetime import datetime

# User must specify these values
obs_data_file = ('path/to/VELMA_Watersheds/Dungeness/Dungeness_Working/Data_Inputs30m/m_7_Observed/'
                 'USGS12048000_Dungeness_nearSequim_streamflow_1981-2021_labeled.csv')
sim_data_file = ('path/to/VELMA_Watersheds/Dungeness/Dungeness_Working/Results/'
                 'MULTI_WA_Dungeness_30m_25Sep2024/Results_72088/DailyResults.csv')
years = range(1990, 1994)
watershed_area = 574907*30*30  # watershed area in square meters

# Filter the desired years into dataframes
sim_df = pd.read_csv(sim_data_file)
sim_df_filtered = sim_df[sim_df['Year'].isin(years)].copy()
sim_df_filtered['Date'] = pd.to_datetime(sim_df_filtered['Year'].astype(str) +
                                         sim_df_filtered['Day'].astype(str), format='%Y%j')
obs_df = pd.read_csv(obs_data_file)
obs_df['Year'] = pd.to_datetime(obs_df['Date']).dt.year
obs_df_filtered = obs_df[obs_df['Year'].isin(years)].copy()
obs_df_filtered['Date'] = pd.to_datetime(obs_df_filtered['Date'].astype(str))

# Extract month-year from date
sim_df_filtered['Month-Year'] = sim_df_filtered['Date'].dt.to_period('M')
obs_df_filtered['Month-Year'] = obs_df_filtered['Date'].dt.to_period('M')

# Calculate the monthly mean as series
sim_monthly_mean = sim_df_filtered.groupby('Month-Year')['Runoff_All(mm/day)_Delineated_Average'].mean()
obs_monthly_mean = obs_df_filtered.groupby('Month-Year')['Runoff-mm'].mean()

# Convert the monthly means from mm to cfs using the watershed area and conversion factors
sim_monthly_mean = sim_monthly_mean*watershed_area/1000/86400*35.3147
obs_monthly_mean = obs_monthly_mean*watershed_area/1000/86400*35.3147

# Turn the series into dataframes
sim_monthly_df = sim_monthly_mean.reset_index()
obs_monthly_df = obs_monthly_mean.reset_index()
sim_monthly_df.columns = ['Month-Year', 'Simulated Mean Discharge, cfs']
obs_monthly_df.columns = ['Month-Year', 'Observed Mean Discharge, cfs']

# Merge the two DataFrames on the 'Month-Year' column
merged_df = pd.merge(sim_monthly_df, obs_monthly_df, on='Month-Year')

# Save the merged DataFrame to a .csv file
merged_df.to_csv(r'path\to\VELMA_Watersheds\Dungeness\Analysis\monthly-means.csv', index=False)

# Plot the two datasets
plt.figure(figsize=(10, 6))
plt.plot(sim_monthly_mean.index.astype(str), sim_monthly_mean, label='Simulated Discharge, cfs', color='b', marker='o')
plt.plot(obs_monthly_mean.index.astype(str), obs_monthly_mean, label='Observed Discharge, cfs', color='r', marker='o')
month_names = obs_monthly_mean.index.strftime('%b')
plt.xticks(ticks=range(len(month_names)), labels=month_names, rotation=45)
plt.xlabel('Month-Year')
plt.ylabel('Mean Monthly Runoff')
plt.legend()
plt.show()

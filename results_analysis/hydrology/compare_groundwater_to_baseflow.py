"""
Explores VELMA's groundwater box ('g-box') behavior against a baseflow
separation (BFS) model. Computes the baseflow fraction from the BFS output and
the groundwater fraction of simulated runoff, with optional comparison plots.
"""

import pandas as pd
import matplotlib.pyplot as plt


# User inputs
bfs_file = r'path\to\VELMA_Watersheds\Hoko\bf_mod_out.12043300.csv'
sim_file = r'path\to\VELMA_Watersheds\Dungeness\Dungeness_Working\Results\WA_Dungeness_30m_9Oct2024/DailyResults.csv'
cell_count = 574907


# Code for dataframes

# 1) Baseflow model
bfs_df = pd.read_csv(bfs_file, usecols=['Date', 'Qob.L3', 'Baseflow.L3'], parse_dates=['Date'])
bfs_df['Qob_cfs'] = bfs_df['Qob.L3'] / 1000
bfs_df['Baseflow_cfs'] = bfs_df['Baseflow.L3'] / 1000
bfs_df['Percent_baseflow'] = bfs_df['Baseflow_cfs'] / bfs_df['Qob_cfs']

# 2) Groundwater box simulation
sim_df = pd.read_csv(sim_file, usecols=['Runoff_All(mm/day)_Delineated_Average',
                                        'Year', 'Day', 'Groundwater_Storage_Removed(mm/day)'])

sim_df['Runoff_cfs'] = (sim_df['Runoff_All(mm/day)_Delineated_Average']/1000)*30*30*cell_count/86400*35.3147
sim_df['Date'] = pd.to_datetime(sim_df['Year'].astype(str) + sim_df['Day'].astype(str).str.zfill(3), format='%Y%j')
sim_df['Groundwater_cfs'] = (sim_df['Groundwater_Storage_Removed(mm/day)']/1000)*30*30/86400*35.3147
sim_df['Percent_groundwater'] = sim_df['Groundwater_cfs'] / sim_df['Runoff_cfs']


# Code for visualizations (you can comment / uncomment blocks below this line)

# BFS magnitude
# plt.figure(figsize=(10, 6))
# plt.plot(bfs_df['Date'], bfs_df['Qob_cfs'], label='Qob (cfs)')
# plt.plot(bfs_df['Date'], bfs_df['Baseflow_cfs'], label='Baseflow (cfs)')
# plt.xlabel('Date')
# plt.ylabel('Flow (cfs)')
# plt.title('Baseflow and Qob over Time')
# plt.legend()
# plt.show()

# BFS percentage
# plt.figure(figsize=(10, 6))
# plt.plot(bfs_df['Date'], bfs_df['Percent_baseflow'], label='% Baseflow')
# plt.xlabel('Date')
# plt.ylabel('Percentage')
# plt.title('Baseflow Percentage Over Time')
# plt.legend()
# plt.show()

# Groundwater magnitude
# plt.figure(figsize=(10, 6))
# plt.plot(sim_df['Date'], sim_df['Runoff_cfs'], label='Runoff (cfs)')
# plt.plot(sim_df['Date'], sim_df['Groundwater_cfs'], label='Groundwater (cfs)')
# plt.xlabel('Date')
# plt.ylabel('Flow (cfs)')
# plt.title('Groundwater and Runoff over Time')
# plt.legend()
# plt.show()

# Groundwater percentage
# plt.figure(figsize=(10, 6))
# plt.plot(sim_df['Date'], sim_df['Percent_groundwater'], label='% Groundwater')
# plt.xlabel('Date')
# plt.ylabel('Percentage')
# plt.title('Groundwater Percentage Over Time')
# plt.legend()
# plt.show()


# Magnitude comparison
plt.figure(figsize=(10, 6))
plt.plot(sim_df['Date'], sim_df['Groundwater_cfs'], label='Sim groundwater (cfs)')
plt.plot(bfs_df['Date'], bfs_df['Baseflow_cfs'], label='Baseflow (cfs)')
plt.xlabel('Date')
plt.ylabel('Flow (cfs)')
plt.title('BFS and Simulated Groundwater Over Time')
plt.legend()
plt.show()

# Percentage comparison
plt.figure(figsize=(10, 6))
plt.plot(sim_df['Date'], sim_df['Percent_groundwater'], label='% Groundwater')
plt.plot(bfs_df['Date'], bfs_df['Percent_baseflow'], label='% Baseflow')
plt.xlabel('Date')
plt.ylabel('Percentage')
plt.title('Groundwater and Baseflow As % Total')
plt.legend()
plt.show()

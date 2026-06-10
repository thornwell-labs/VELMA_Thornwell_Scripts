"""
Compares simulated flow from multiple VELMA results folders against observed
data, converting runoff to cfs and computing the groundwater fraction of
runoff. NOTE: incomplete/broken as written — `sim_file` is undefined (only
sim_file1-3 are defined) and matplotlib is imported incorrectly.
"""

import pandas as pd
import matplotlib as plt

sim_file1 = 'path/to/network_share/Dungeness_Data/Results/WA_Dungeness_30m_27Sep2024/DailyResults.csv'
sim_file2 = ''
sim_file3 = ''
cell_count = 574907

sim_df = pd.read_csv(sim_file, usecols=['Runoff_All(mm/day)_Delineated_Average',
                                        'Year', 'Day', 'Groundwater_Storage_Removed(mm/day)'])

sim_df['Runoff_cfs'] = (sim_df['Runoff_All(mm/day)_Delineated_Average']/1000)*30*30*cell_count/86400*35.3147
sim_df['Date'] = pd.to_datetime(sim_df['Year'].astype(str) + sim_df['Day'].astype(str).str.zfill(3), format='%Y%j')
sim_df['Groundwater_cfs'] = (sim_df['Groundwater_Storage_Removed(mm/day)']/1000)*30*30/86400*35.3147
sim_df['Percent_groundwater'] = sim_df['Groundwater_cfs'] / sim_df['Runoff_cfs']

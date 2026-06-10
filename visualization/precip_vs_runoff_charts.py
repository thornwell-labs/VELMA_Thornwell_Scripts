"""
Plots day-of-year average precipitation against simulated runoff on a dual-axis
chart for one watershed, using a 7-day rolling mean, to visualize the
precipitation-runoff seasonal relationship. Companion to
runoff_vs_precip_plots.py.
"""

import pandas as pd
import matplotlib.pyplot as plt

precip_filepath = 'path/to/VELMA_Watersheds/Huge/Data_Inputs30m/m_2_Weather/2_SpatialModel/Huge_Historic1987_2005_Future2006_2099_archive/Average_Precip_ByDate_archive.csv'
results_filepaths = ['path/to/PSIMF Management/Proof_of_Concept_QC/2019_Results/BigBeef_21July2025_VELMA_to_SSM.csv',
                     'path/to/PSIMF Management/Proof_of_Concept_QC/2029_Results/BigBeef_2029_VELMA_to_SSM.csv']
start_date = '2006-01-01'
end_date = '2029-12-31'
watershed = 'Huge'

precip_df = pd.read_csv(precip_filepath, index_col='Date', parse_dates=['Date'])
precip_df_filtered = precip_df.loc[start_date:end_date]
precip_data_1yr = precip_df_filtered['Precip_avg']
precip_data_1yr_gp=precip_data_1yr.rolling(window=7).mean().groupby(precip_data_1yr.index.dayofyear).mean()

# runoff_data_1yr = pd.Series(dtype=float)
# for results_path in results_filepaths:
#     runoff_df = pd.read_csv(results_path, usecols=['Date', 'Runoff(m3/s)'], index_col='Date', parse_dates=['Date'])
#     runoff_df_filtered = runoff_df.loc[start_date:end_date]
#     runoff_data_1yr = pd.concat([runoff_data_1yr, runoff_df_filtered['Runoff(m3/s)']])
# runoff_data_1yr_gp=runoff_data_1yr.rolling(window=7).mean().groupby(runoff_data_1yr.index.dayofyear).mean()

fig, ax1 = plt.subplots()

# Left y-axis: precipitation
ax1.plot(precip_data_1yr_gp.index, precip_data_1yr_gp.values, color='blue', alpha=0.5, label='Precipitation')
ax1.set_xlabel('Julian Day')
ax1.set_ylabel('Precipitation (in)', color='blue')

# Right y-axis: runoff
# ax2 = ax1.twinx()
# ax2.plot(runoff_data_1yr_gp.index, runoff_data_1yr_gp.values, color='green', label='Runoff')
# ax2.set_ylabel('Runoff (m3/s)', color='green')

plt.title(f'Rolling 7-Day Average Precip from {start_date} to {end_date} in {watershed}')
plt.show()
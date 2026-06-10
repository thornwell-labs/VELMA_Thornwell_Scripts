"""
Compares VELMA-simulated water surface temperature to observed temperature at
a single USGS gage. Single-location variant of compare_usgs_temperature.py;
aligns the daily series by date and reports R^2 with a comparison plot.
"""

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
import os

observed_folder ="path/to/VELMA_Watersheds/Snohomish/Data_Inputs30m/m_7_Observed/USGS_Temperature"
simulated_folder = "path/to/VELMA_Watersheds/Snohomish/Results/MULTI_WA_Snohomish30m_Penumbra_Historical_USGS_12148500"
output_folder = "path/to/VELMA_Watersheds/Snohomish/Analysis/USGS Temperature Comparison"
watershed_name = 'Snohomish'

gage = '12147600'
cell_index = '6733527'
output_file = f'{output_folder}/{watershed_name}_{gage}_30m'


observed_temp_file = f'{observed_folder}/USGS_{gage}.csv'
observed_df = pd.read_csv(observed_temp_file, parse_dates=['Date'])
simulated_subfolder = f'{simulated_folder}/Results_{cell_index}'
simulated_temp_file = None
for fname in os.listdir(simulated_subfolder):
    if 'dlnWriter.csv' in fname:
        simulated_temp_file = os.path.join(simulated_subfolder, fname)
        break
simulated_df = pd.read_csv(simulated_temp_file, usecols=['Year', 'Jday', 'Water_Surface_Temperature(degrees_C)'])

simulated_df['Date'] = pd.to_datetime(simulated_df['Year'].astype(str), format='%Y') + pd.to_timedelta(simulated_df['Jday'] - 1, unit='D')

observed_df.set_index('Date', inplace=True)
simulated_df.set_index('Date', inplace=True)

valid_dates = observed_df['Mean Temp'].dropna().index
sim_filtered = simulated_df.loc[simulated_df.index.isin(valid_dates)]
obs_filtered = observed_df.loc[observed_df.index.isin(valid_dates)]

combined_df = pd.DataFrame({
    'Observed': obs_filtered['Mean Temp'],
    'Simulated': sim_filtered['Water_Surface_Temperature(degrees_C)']
}).dropna()

print(f"Observed mean: {combined_df['Observed'].mean()}, Simulated mean: {combined_df['Simulated'].mean()}")
print(f"Observed std: {combined_df['Observed'].std()}, Simulated std: {combined_df['Simulated'].std()}")

combined_df['Observed_7day'] = combined_df['Observed'].rolling(window=7, center=True).mean()
combined_df['Simulated_7day'] = combined_df['Simulated'].rolling(window=7, center=True).mean()

combined_df = combined_df

combined_df = combined_df.dropna(subset=['Observed_7day', 'Simulated_7day'])

# start_date = '2016-09-07'
# end_date   = '2020-01-10'
# combined_df = combined_df.loc[start_date:end_date]

r2 = r2_score(combined_df['Observed_7day'], combined_df['Simulated_7day'])

# Identify gaps in time and insert NaN where there are gaps
time_diff = combined_df.index.to_series().diff()
gap_mask = time_diff > pd.Timedelta(days=1)
combined_df.loc[gap_mask, ['Observed_7day', 'Simulated_7day']] = pd.NA


plt.figure(figsize=(12,6))
plt.plot(
    combined_df.index,
    combined_df['Simulated_7day'],
    label='Simulated (7-day avg)',
    color='tab:blue',
    linewidth=2
)
plt.plot(
    combined_df.index,
    combined_df['Observed_7day'],
    label='Observed (7-day avg)',
    color='tab:orange',
    linewidth=2
)

plt.xlabel('Date')
plt.ylabel('Temperature (°C)')
plt.title(f'Observed vs Simulated 7-Day Running Average Water Temperature \n {watershed_name} USGS Gage {gage} \n $R^2$ = {r2:.3f}')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(output_file)
plt.show()

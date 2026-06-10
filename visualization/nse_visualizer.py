"""
Plots observed and simulated runoff together for selected year(s) and
annotates each year with its Nash-Sutcliffe Efficiency (NSE), giving a visual
read on calibration quality over time.
"""

# This file plots observed and simulated runoff on the same plot for specified year(s) and labels the NSE of each year.

import pandas as pd
import matplotlib.pyplot as plt
import statistics
from datetime import datetime

# User must specify these values
obs_data_file = ('path/to/VELMA_Watersheds/Skagit/Data_Inputs30m/m_7_Observed/'
                 'USGS12189500_SaukRiver_nearSauk_streamflow_1981-2021_labeled.csv')
sim_data_file = ('path/to/VELMA_Watersheds/Skagit/Results/WA_Skagit30m_30May2025_resampled_3_Hyak/Results_1901652/DailyResults.csv')
years = range(1998, 2003)

# This block takes care of title formatting
years_string = ''
for year in years:
    if len(years_string) == 0:
        years_string = f'{year}'
    else:
        years_string = years_string+f', {year}'
    if len(years) >= 5:
        years_string = f'{years[0]} to {years[-1]}'

# Filter the desired years into dataframes
sim_df = pd.read_csv(sim_data_file)
sim_df_filtered = sim_df[sim_df['Year'].isin(years)].copy()
sim_df_filtered['Date'] = pd.to_datetime(sim_df_filtered['Year'].astype(str) +
                                         sim_df_filtered['Day'].astype(str), format='%Y%j')
obs_df = pd.read_csv(obs_data_file)
obs_df['Year'] = pd.to_datetime(obs_df['Date']).dt.year
obs_df_filtered = obs_df[obs_df['Year'].isin(years)].copy()
obs_df_filtered['Date'] = pd.to_datetime(obs_df_filtered['Date'].astype(str))


# This block of code plots the simulated and observed runoff in millimeters
plt.figure(figsize=(10, 6))
plt.plot(sim_df_filtered['Date'], sim_df_filtered['Runoff_All(mm/day)_Delineated_Average'],
         label='Simulated', linewidth=2, alpha=0.7)
plt.plot(obs_df_filtered['Date'], obs_df_filtered['Runoff-mm'],
         label='Observed', linewidth=2, alpha=0.7)
plt.ylabel('Runoff (mm)')
plt.title(f'Observed and Simulated Runoff for {years_string}')


# This code determines the dates that have both observed and simulated runoff and aligns them
aligned_data = pd.merge(sim_df_filtered[['Date', 'Runoff_All(mm/day)_Delineated_Average']],
                        obs_df_filtered[['Date', 'Runoff-mm']],
                        on='Date', how='inner')
simulated_runoff = aligned_data['Runoff_All(mm/day)_Delineated_Average']
observed_runoff = aligned_data['Runoff-mm']

sim_df_filtered.to_csv(f'path/to/output/simulated_data.csv',
                       columns=['Date', 'Year', 'Day', 'Runoff_All(mm/day)_Delineated_Average'])
obs_df_filtered.to_csv(f'path/to/output/observed_data.csv')
aligned_data.to_csv(f'path/to/output/aligned_data.csv')


# This block of code calculates NSE by season
def calculate_nse(df, season_start, season_end):
    season_data = df[(df['Date'] >= season_start) & (df['Date'] <= season_end)]
    season_data.reset_index(drop=True, inplace=True)
    variance = (season_data['Runoff-mm'] - season_data['Runoff-mm'].mean()) ** 2
    error_variance = (season_data['Runoff-mm'] - season_data['Runoff_All(mm/day)_Delineated_Average']) ** 2
    nse = 1 - (error_variance.sum() / variance.sum())
    nse = round(nse, 2)
    
    if nse < 0:
        season_data.to_csv(f'path/to/output/{season_start}_nse_{nse}.csv')

    return nse


# nse_seasons = {
#     'spring': [],
#     'summer': [],
#     'fall': [],
#     'winter': []
# }

# for year in years:
#     spring_start, spring_end = f'{year}-03-01', f'{year}-05-31'
#     summer_start, summer_end = f'{year}-06-01', f'{year}-08-31'
#     fall_start, fall_end = f'{year}-09-01', f'{year}-11-30'
#     winter_start, winter_end = f'{year}-12-01', f'{year + 1}-02-28'

#     nse_spring = calculate_nse(aligned_data, spring_start, spring_end)
#     nse_seasons['spring'].append(nse_spring)
#     plt.annotate(f'Spring: {nse_spring}', xy=(datetime(year, 4, 1), 0.80),
#                  xytext=(datetime(year, 4, 1), 60), fontsize=8, ha='center')
#     nse_summer = calculate_nse(aligned_data, summer_start, summer_end)
#     nse_seasons['summer'].append(nse_summer)
#     plt.annotate(f'Summer: {nse_summer}', xy=(datetime(year, 4, 1), 0.80),
#                  xytext=(datetime(year, 7, 1), 60), fontsize=8, ha='center')
#     nse_fall = calculate_nse(aligned_data, fall_start, fall_end)
#     nse_seasons['fall'].append(nse_fall)
#     plt.annotate(f'Fall: {nse_fall}', xy=(datetime(year, 4, 1), 0.80),
#                  xytext=(datetime(year, 10, 1), 60), fontsize=8, ha='center')
#     nse_winter = calculate_nse(aligned_data, winter_start, winter_end)
#     nse_seasons['winter'].append(nse_winter)
#     plt.annotate(f'Winter: {nse_winter}', xy=(datetime(year, 4, 1), 0.80),
#                  xytext=(datetime(year+1, 1, 1), 60), fontsize=8, ha='center')

# for season, nse_list in nse_seasons.items():
#     print(f"NSE for {season}: {nse_list}")
#     print(f"Average NSE for {season}: {round(statistics.mean(nse_list), 2)}")


# This block of code annotates the data with NSE values for each year
# nse_df = pd.read_csv('path/to/VELMA_Watersheds/Elwha/Elwha_Working/Results/'
#                      'documents_20240826/AnnualHydrologyResults.csv')
# nse_dict = nse_df.set_index('YEAR')['Runoff_Nash-Sutcliffe_Coefficient'].to_dict()
# for year in years:
#     nse_value = round(nse_dict.get(year), 2)
#     start_date = datetime(year, 1, 1)
#     end_date = datetime(year, 12, 31)
#     middle_date = datetime(year, 6, 30)
#     y_placement = max(sim_df_filtered['Runoff_All(mm/day)_Delineated_Average'])
#     plt.annotate(f'NSE={nse_value}', xy=(middle_date, y_placement), xytext=(middle_date, y_placement+0.5),
#                  fontsize=8,  ha='center')


plt.xlabel('Date')
plt.legend()
plt.grid(True)
plt.show()

"""
Calculates summer-only Nash-Sutcliffe Efficiency (NSE) for a VELMA run against
observed USGS streamflow. Aligns simulated and observed daily series by date
and computes NSE over the summer months of each year.
"""

import pandas as pd
import numpy as np

# Define these required variables and file paths
working_directory = 'path/to/VELMA_Watersheds/Samish'
results_folder_root = f'{working_directory}/Results'
observed_file = f'{working_directory}/Data_Inputs30m/m_7_Observed/USGS12201500_Samish_nearBurlington_streamflow_1981-2021.csv'
calibration_data = 'Runoff_All(mm/day)_Delineated_Average'  # must EXACTLY match a column in the DailyResults file
start_obs_data_year = 1981  # Enter the year the observed data starts from (be sure to check the observed data file)
results_path = f'{results_folder_root}/Samish_09Jan2024/DailyResults.csv'  # must be DailyResults.csv


# Read in the observed data and assign an index by date
observed_df = pd.read_csv(observed_file, usecols=[0], header=None, names=[calibration_data])
start_date = f'1/1/{start_obs_data_year}'
date_range = pd.date_range(start=start_date, periods=len(observed_df), freq='D')
observed_df['Date'] = date_range
observed_df.set_index('Date', inplace=True)

# Read in any DailyResults file and return dataframe of calibration data indexed by date
def results_interpreter(csv_path):
    results_df = pd.read_csv(csv_path, usecols=['Year', 'Day', calibration_data])
    start_year = results_df['Year'].iloc[0]
    start_date = f'1/1/{start_year}'
    date_range = pd.date_range(start=start_date, periods=len(results_df), freq='D')
    results_df['Date'] = date_range
    results_df.set_index('Date', inplace=True)
    results_df = results_df.drop(columns=['Year', 'Day'])
    return results_df

def align_group_data(observed_df, results_df):
    aligned = results_df.join(observed_df, lsuffix='_sim', rsuffix='_obs')
    aligned = aligned.dropna()
    grouped = aligned.groupby(aligned.index.year)
    for year, data in grouped:
        if len(data) < 315:
            print(f'WARNING: observed data in year {year} is missing 50+ values.')
    return grouped

def calculate_nse_summer(grouped_data):
    nse_summer_by_year = {}
    for year, data in grouped_data:
        obs = data[f'{calibration_data}_obs'][data.index.month.isin([6, 7, 8, 9])]  # Filter months for June through September
        sim = data[f'{calibration_data}_sim'][data.index.month.isin([6, 7, 8, 9])]
        obs_mean = np.mean(obs)
        sim_mean = np.mean(sim)
        numerator = np.sum((obs - obs_mean) * (sim - sim_mean)) ** 2
        denominator = np.sum((obs - obs_mean) ** 2) * np.sum((sim - sim_mean) ** 2)
        nse_summer_by_year[year] = numerator / denominator
    return nse_summer_by_year

results_df = results_interpreter(results_path)
grouped_data = align_group_data(observed_df, results_df)
nse_summer_dict = calculate_nse_summer(grouped_data)
for year, nse in nse_summer_dict.items():
    print(f'{year},{round(nse,3)}')

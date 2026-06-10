"""
Compares VELMA-simulated water surface temperature to observed USGS gage
temperatures at multiple locations. Uses a key CSV mapping each USGS gage to
its VELMA cell index, aligns the series by date, and reports R^2 with
comparison plots for each gage. See the _single variant for one gage.
"""

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
import os

key_file =r"path\to\VELMA_Watersheds\Skokomish\Analysis\USGS Temperature Comparison\Skokomish_USGS_VELMA_90m_key.csv"
observed_folder = r"path\to\VELMA_Watersheds\Skokomish\Data_Inputs30m\m_7_Observed\USGS_Temperature"
simulated_folder = r"path\to\VELMA_Watersheds\Skokomish\Results\MULTI_WA_Skokomish30m_Historical_resampled_3_Penumbra"
output_folder = r"path\to\VELMA_Watersheds\Skokomish\Analysis\USGS Temperature Comparison"
watershed_name = 'Skokomish'


key_df = pd.read_csv(key_file)
key_dict = {str(row['USGS Gage']): str(row['VELMA index (3x)']) for _, row in key_df.iterrows()}

for gage, cell_index in key_dict.items():
    observed_temp_file = f'{observed_folder}/USGS_{gage}_Temperature_Raw.csv'
    observed_df = pd.read_csv(observed_temp_file, parse_dates=['Date'])
    simulated_temp_file = None
    for dirpath, dirnames, filenames in os.walk(simulated_folder):
        for fname in filenames:
            if str(cell_index) in fname:
                simulated_temp_file = os.path.join(dirpath, fname)
                break
    if simulated_temp_file is None:
        print(f"No simulated results file found for USGS gage {gage}.")
        continue
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

    combined_df = combined_df.dropna(subset=['Observed_7day', 'Simulated_7day'])

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
        linewidth=2
    )
    plt.plot(
        combined_df.index,
        combined_df['Observed_7day'],
        label='Observed (7-day avg)',
        linewidth=2
    )

    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.title(f'Observed vs Simulated 7-Day Running Average Water Temperature \n {watershed_name} USGS Gage {gage} \n $R^2$ = {r2:.3f}')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    output_file = f'{output_folder}/{watershed_name}_{gage}'
    plt.savefig(output_file)
    # plt.show()

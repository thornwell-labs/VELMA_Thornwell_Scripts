"""
Compares VELMA-simulated snow depth to observed SNOTEL snow water equivalent
at a station location. Plots the two series together and writes a CSV of the
aligned simulated and observed data.
"""

import pandas as pd
import os
import matplotlib.pyplot as plt

snotel_name = 'Skookum_Creek_1995-2019'
output_folder = 'path/to/VELMA_Watersheds/Snohomish/Analysis/'
obs_folder = 'path/to/VELMA_Watersheds/Snohomish/Data_Inputs30m/m_7_Observed/SNOTEL/'
velma_results = r"path\to\VELMA_Watersheds\Snohomish\Results\MULTI_WA_Snohomish30m_Penumbra_Historical_resampled_3\Cell_i777695_x572_y711_Skookum.csv"

# Make sure the output directory exists
os.makedirs(output_folder, exist_ok=True)

# Read in the VELMA results and check whether it's a daily results or cell data writer file
if 'DailyResults' in velma_results:
    day_key = 'Day'
    snow_key = 'Snow_Depth(mm)_Delineated_Average'
elif 'Cell' in velma_results:
    day_key = 'Jday'
    snow_key = 'Snow_Depth(mm)'
    
sim_df = pd.read_csv(velma_results, usecols=['Year', day_key, snow_key])
sim_df['Date'] = pd.to_datetime(sim_df['Year'].astype(str), format='%Y') + pd.to_timedelta(sim_df[day_key], unit='D')


obs_list = []
for file in os.listdir(obs_folder):
    if snotel_name in file:
        filepath = os.path.join(obs_folder, file)
        df = pd.read_csv(filepath, usecols=['Date', 'Snow Water Equivalent (in) Start of Day Values'], parse_dates=['Date'])
        df.columns = ['Date', 'Snow_Depth_in']
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)
        df['Snow_Depth_mm'] = df['Snow_Depth_in'] * 25.4  # Convert inches to mm
        df = df[df['Snow_Depth_mm'] >= 0]  # Drop negative values
        obs_list.append(df[['Date', 'Snow_Depth_mm']])
            
# Concatenate all observed data
obs_df = pd.concat(obs_list, ignore_index=True)

# Output observed data to a single file
obs_output_path = os.path.join(obs_folder, f'{snotel_name}_observed.csv')
obs_df.to_csv(obs_output_path, index=False)
print(f"Combined observed snow depth saved to: {obs_output_path}")

# Merge observed and simulated data on date
merged_df = pd.merge(sim_df[['Date', snow_key]],
                     obs_df,
                     on='Date', how='inner')

# Save merged dataframe to CSV
csv_path = os.path.join(output_folder, f'{snotel_name}_Snotel_Comparison.csv')
merged_df.to_csv(csv_path, index=False)
print(f"Merged data saved to: {csv_path}")


# Plotting
plt.figure(figsize=(12, 6))
plt.plot(merged_df['Date'], merged_df[snow_key], label='Simulated (VELMA)', color='blue')
plt.plot(merged_df['Date'], merged_df['Snow_Depth_mm'], label='Observed (SNOTEL)', color='orange')
plt.xlabel('Date')
plt.ylabel('Snow Depth (mm)')
plt.title(f'Simulated vs Observed Snow Depth at {snotel_name.replace('_',' ')}')
plt.legend()
plt.tight_layout()

# Save the plot
plot_path = os.path.join(output_folder, f'{snotel_name}_Sim_vs_Observed_SnowDepth.png')
plt.savefig(plot_path)
print(f"Plot saved to: {plot_path}")

# Show the plot
plt.show()

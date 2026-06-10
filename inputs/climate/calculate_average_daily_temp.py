"""
Computes the watershed-average daily air temperature time series from VELMA
spatial weather driver files. Averages the temperature column across all
Site*.csv files in each weather model folder and writes
Average_Temp_ByDate.csv. Companion to calculate_average_daily_precip.py.
"""

import pandas as pd
import os

data_folders = [
    'path/to/VELMA_Watersheds/Mercer/Data_Inputs30m/m_2_Weather/2_SpatialModel/Mercer_30m_800m_Historic__PRISM_1981_2021',
    'path/to/VELMA_Watersheds/Skokomish/Data_Inputs30m/m_2_Weather/2_SpatialModel/Skokomish_30m_800m_Historic__PRISM_1981_2021'
]

date_series = None

for data_folder in data_folders:
    temp_sum = None
    site_count = 0
    for root, dirs, files in os.walk(data_folder):
        for file in files:
            if "Site" in file and file.endswith(".csv"):
                filepath = os.path.join(root, file)
                
                # Read site data
                df = pd.read_csv(filepath, header=None, names=['Year', 'Jday', 'Precip', 'Temp'])
                df = df.drop(columns=['Precip'])
                
                # Build Date column
                df['Date'] = pd.to_datetime(
                    df['Year'].astype(int).astype(str) + df['Jday'].astype(int).astype(str),
                    format="%Y%j"
                )
                
                if temp_sum is None:
                    # First site initializes sum and date
                    temp_sum = df['Temp'].copy()
                    date_series = df['Date']
                else:
                    # Add to running sum
                    temp_sum += df['Temp']
                
                site_count += 1
                print(f"Processed {file} ({site_count} sites)")

    # Compute average
    if temp_sum is not None and site_count > 0:
        result = pd.DataFrame({
            'Date': date_series,
            'Temp_avg': temp_sum / site_count
        })
        
        out_path = os.path.join(data_folder, "Average_Temp_ByDate.csv")
        result.to_csv(out_path, index=False)
        print(f"Saved average temperature to {out_path}")
    else:
        print("No site files found.")

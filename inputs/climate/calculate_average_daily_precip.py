"""
Computes the watershed-average daily precipitation time series from VELMA
spatial weather driver files. Walks a weather model folder, averages the
precipitation column across all Site*.csv files, and writes
Average_Precip_ByDate.csv. See the _multicore variant for parallel processing
of multiple watersheds.
"""

import pandas as pd
import os

data_folders = [
    'path/to/hpc/Deschutes/Data_Inputs30m/m_2_Weather/2_SpatialModel/Deschutes_Historic1987_2005_Future2006_2099/'    
]
site_count = 0
precip_sum = None
date_series = None

for data_folder in data_folders:
    precip_sum = None
    site_count = 0
    for root, dirs, files in os.walk(data_folder):
        for file in files:
            if "Site" in file and file.endswith(".csv"):
                filepath = os.path.join(root, file)
                
                # Read site data
                df = pd.read_csv(filepath, header=None, names=['Year', 'Jday', 'Precip', 'Temp'])
                df = df.drop(columns=['Temp'])
                
                # Build Date column safely
                try:
                    # Only proceed if required columns exist
                    if 'Year' in df.columns and 'Jday' in df.columns:
                        # Convert to datetime, coercing bad rows to NaT instead of erroring out
                        df['Date'] = pd.to_datetime(
                            df['Year'].astype(str) + df['Jday'].astype(str).str.zfill(3),
                            format='%Y%j',
                            errors='coerce'
                        )
                        # Drop rows where the date could not be parsed
                        df = df.dropna(subset=['Date'])
                    else:
                        print(f"Skipping file {file}: missing 'Year' or 'Jday' column.")
                        continue
                except Exception as e:
                    print(f"Skipping file {file} due to date parsing error: {e}")
                    continue
                
                if precip_sum is None:
                    # First site initializes sum and date
                    precip_sum = df['Precip'].copy()
                    date_series = df['Date']
                else:
                    # Add to running sum
                    precip_sum += df['Precip']
                
                site_count += 1
                print(f"Processed {file} ({site_count} sites)")

    # Compute average
    if precip_sum is not None and site_count > 0:
        result = pd.DataFrame({
            'Date': date_series,
            'Precip_avg': precip_sum / site_count
        })
        
        out_path = os.path.join(data_folder, "Average_Precip_ByDate.csv")
        result.to_csv(out_path, index=False)
        print(f"Saved average precip to {out_path}")
    else:
        print("No site files found.")

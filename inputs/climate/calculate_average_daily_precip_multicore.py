"""
Parallel version of calculate_average_daily_precip.py. Computes the
watershed-average daily precipitation series from VELMA Site*.csv weather
driver files, processing multiple watershed folders concurrently with a
multiprocessing pool and writing Average_Precip_ByDate.csv into each folder.
"""

import pandas as pd
import os
from multiprocessing import Pool

def process_watershed(data_folder):
    """Compute average daily precipitation across all Site*.csv files in one watershed."""
    precip_sum = None
    date_series = None
    site_count = 0

    for root, _, files in os.walk(data_folder):
        for file in files:
            if "Site" not in file or not file.endswith(".csv"):
                continue

            filepath = os.path.join(root, file)

            # Read only the needed columns
            try:
                df = pd.read_csv(
                    filepath,
                    usecols=[0, 1, 2],
                    header=None,
                    names=['Year', 'Jday', 'Precip']
                )
            except Exception as e:
                print(f"Skipping {file} due to read error: {e}")
                continue

            # Safely build Date column
            df['Date'] = pd.to_datetime(
                df['Year'].astype(str) + df['Jday'].astype(str).str.zfill(3),
                format='%Y%j',
                errors='coerce'
            )
            df = df.dropna(subset=['Date'])

            # Convert Precip to numeric, fill missing with 0
            df['Precip'] = pd.to_numeric(df['Precip'], errors='coerce').fillna(0.0)

            # Initialize or accumulate precipitation
            if precip_sum is None:
                precip_sum = df['Precip'].copy()
                date_series = df['Date']
            else:
                precip_sum = precip_sum.add(df['Precip'], fill_value=0)

            site_count += 1
            if site_count % 50 == 0:
                print(f"{os.path.basename(data_folder)}: processed {site_count:,} sites...")

    # Save results
    if site_count > 0 and precip_sum is not None:
        result = pd.DataFrame({
            'Date': date_series,
            'Precip_avg': precip_sum / site_count
        })
        out_path = os.path.join(data_folder, "Average_Precip_ByDate.csv")
        result.to_csv(out_path, index=False)
        print(f"✅ {os.path.basename(data_folder)}: saved average from {site_count:,} sites to {out_path}")
    else:
        print(f"⚠️ {os.path.basename(data_folder)}: no valid site files found.")


def main():
    # Add all your watershed directories here
    data_folders = [
        # 'path/to/hpc/Deschutes/Data_Inputs30m/m_2_Weather/2_SpatialModel/Deschutes_Historic1987_2005_Future2006_2099/',
        'path/to/VELMA_Watersheds/Huge/Data_Inputs30m/m_2_Weather/2_SpatialModel/Huge_Historic1987_2005_Future2006_2099',
        'path/to/VELMA_Watersheds/Hoko/Data_Inputs30m/m_2_Weather/2_SpatialModel/Hoko_Historic1987_2005_Future2006_2099'
        # Add additional folders as needed...
    ]

    # --- Option 1: Sequential processing ---
    # for folder in data_folders:
    #     process_watershed(folder)

    # --- Option 2: Parallel processing (one per core) ---
    num_workers = min(len(data_folders), os.cpu_count() or 1)
    with Pool(processes=num_workers) as pool:
        pool.map(process_watershed, data_folders)


if __name__ == "__main__":
    main()

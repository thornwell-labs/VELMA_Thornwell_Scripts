"""
Summarizes how watershed-average precipitation changes by decade. Reads the
Average_Precip_ByDate.csv files produced by calculate_average_daily_precip.py
and writes a per-watershed summary comparing each future decade to the
historical baseline.
"""

import os
import pandas as pd

full_files = [
    'path/to/VELMA_Watersheds/Deschutes/Data_Inputs30m/m_2_Weather/2_SpatialModel/Deschutes_Historic1987_2005_Future2006_2099/Average_Precip_ByDate.csv',
    'path/to/VELMA_Watersheds/Hoko/Data_Inputs30m/m_2_Weather/2_SpatialModel/Hoko_Historic1987_2005_Future2006_2099/Average_Precip_ByDate.csv',
    'path/to/VELMA_Watersheds/Huge/Data_Inputs30m/m_2_Weather/2_SpatialModel/Huge_Historic1987_2005_Future2006_2099/Average_Precip_ByDate.csv'
]

out_folder = 'path/to/PSIMF Management/Proof_of_Concept_QC'
os.makedirs(out_folder, exist_ok=True)

def infer_watershed_from_path(filepath):
    """
    Try to find a folder segment that contains '_Historic' and return the prefix
    (e.g., 'Deschutes_Historic...' -> 'Deschutes').
    If not found, fall back to the grandparent folder name, then parent folder name.
    """
    parts = os.path.normpath(filepath).split(os.sep)
    for p in parts:
        if '_Historic' in p:
            return p.split('_Historic')[0]
    # fallback candidates
    if len(parts) >= 3:
        return parts[-3]  # e.g., .../VELMA_Watersheds/<Watershed>/Data_Inputs30m/...
    elif len(parts) >= 2:
        return parts[-2]
    else:
        return os.path.splitext(os.path.basename(filepath))[0]

summary_rows = []  # list of dicts, one per watershed
decade_labels = ['2020s','2030s','2040s','2050s','2060s','2070s','2080s','2090s']

for file in full_files:
    try:
        name = infer_watershed_from_path(file)
        print(f'Processing {name} -> {file}')

        df = pd.read_csv(file, parse_dates=['Date'], low_memory=False)
        if 'Precip_avg' not in df.columns:
            print(f"  Skipping {name}: missing 'Precip_avg' column.")
            continue

        # Compute annual precipitation totals
        df['Year'] = df['Date'].dt.year
        annual_precip = df.groupby('Year', sort=True)['Precip_avg'].sum()

        # Historic baseline: 2010–2019
        hist_years = annual_precip.loc[(annual_precip.index >= 2010) & (annual_precip.index <= 2019)]
        if hist_years.empty:
            print(f"  Skipping {name}: no data from 2010–2019 for baseline.")
            continue
        hist_mean = hist_years.mean()

        if hist_mean == 0 or pd.isna(hist_mean):
            print(f"  Skipping {name}: historic mean is zero or NaN (cannot compute percent diffs).")
            continue

        # Compute percent difference for each decade (2020–2029, 2030–2039, etc.)
        decade_ranges = [(2020, 2029), (2030, 2039), (2040, 2049), (2050, 2059),
                         (2060, 2069), (2070, 2079), (2080, 2089), (2090, 2099)]

        decade_diffs = {label: pd.NA for label in decade_labels}
        for (start, end), label in zip(decade_ranges, decade_labels):
            decade_data = annual_precip.loc[(annual_precip.index >= start) & (annual_precip.index <= end)]
            if not decade_data.empty:
                dec_mean = decade_data.mean()
                # Avoid division-by-zero and ensure numeric
                if pd.isna(dec_mean):
                    print(f"    {name}: decade {label} mean is NaN, skipping.")
                    continue
                percent_diff = ((dec_mean - hist_mean) / hist_mean) * 100
                decade_diffs[label] = percent_diff

        # Save per-watershed results (one CSV per watershed)
        decadal_df = pd.DataFrame(list(decade_diffs.items()), columns=['Decade', 'PercentDiff']).set_index('Decade')
        decadal_df.to_csv(os.path.join(out_folder, f'{name}_decadal_precip_change.csv'))

        # Add to summary rows with watershed name as first column
        row = {'Watershed': name}
        row.update(decade_diffs)  # labels become columns
        summary_rows.append(row)

    except Exception as e:
        print(f"Error processing {file}: {e}")
        continue

# === Combine into summary table (watersheds as rows, decades as columns) ===
if summary_rows:
    summary_df = pd.DataFrame(summary_rows)
    # Ensure column order: Watershed first, then decades in chronological order
    cols = ['Watershed'] + decade_labels
    # Add any missing columns with NA so reindex won't fail
    for c in cols:
        if c not in summary_df.columns:
            summary_df[c] = pd.NA
    summary_df = summary_df[cols]
    summary_csv = os.path.join(out_folder, 'decadal_precip_change_summary.csv')
    summary_df.to_csv(summary_csv, index=False)
    print(f"/nCombined summary saved to: {summary_csv}")
    print(summary_df.round(2))
else:
    print("No valid precipitation data found. Summary not created.")

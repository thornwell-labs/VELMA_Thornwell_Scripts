"""
Plots SSM-format VELMA results for each watershed across the historical
baseline and each future decade, producing per-watershed comparison figures
for the PSIMF proof-of-concept QC.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

base_path = 'path/to/PSIMF Management/Proof_of_Concept_QC'
folder_path_2019 = os.path.join(base_path, '2019_Results')
figure_path = os.path.join(base_path, 'Figures')

# Define which future decades to include
decades = [2029, 2039, 2049, 2059, 2069, 2079, 2089, 2099]

# Build dictionary of {label: folder_path}, include baseline
folders = {"1987–2019": folder_path_2019}
folders.update({decade: os.path.join(base_path, f"{decade}_Results") for decade in decades})

# Loop through the folders to drive watershed discovery
for decade_label, folder_path in list(folders.items()):
    if not os.path.exists(folder_path):
        print(f"Skipping {decade_label}, no folder found at {folder_path}")
        continue

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith('.csv'):
                name = filename.split('_')[0]

                # --- collect dataframes for this watershed ---
                dfs = {}
                for label, fpath in folders.items():
                    if not os.path.exists(fpath):
                        continue
                    match_file = None
                    for f in os.listdir(fpath):
                        if name in f and f.endswith('.csv'):
                            match_file = os.path.join(fpath, f)
                            break
                    if match_file:
                        dfs[label] = pd.read_csv(match_file, parse_dates=['Date'], index_col='Date')

                if "1987–2019" not in dfs:
                    print(f"Skipping {name}, no 2019 baseline found")
                    continue

                # Find common columns across all decades
                common_cols = set.intersection(*(set(df.columns) for df in dfs.values()))

                # --- plot all decades together ---
                outdir = os.path.join(figure_path, name)
                os.makedirs(outdir, exist_ok=True)

                for col in common_cols:
                    plt.figure(figsize=(10, 6))
                    for label, df in dfs.items():
                        plt.plot(df.index, df[col], label=label)
                    plt.xlabel('Date')
                    plt.ylabel(col)
                    plt.title(f'{col} in {name}')
                    plt.legend()

                    # sanitize column name for filename
                    col_sanitized = col.replace('/', '_')
                    plt.savefig(os.path.join(outdir, f'{col_sanitized}.png'))
                    plt.close()
                    
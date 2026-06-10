"""
Overlays common columns from multiple SSM-format result CSVs on shared plots,
one figure per variable, to compare runs (e.g. different initializations or
scenarios) side by side.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

base_path = 'path/to/VELMA_Watersheds/Huge/Analysis/Spatial Pool Comparison'
figure_path = os.path.join(base_path, 'Figures')
os.makedirs(figure_path, exist_ok=True)

# Step 1: collect all CSVs
dfs = {}
for root, dirs, files in os.walk(base_path):
    for filename in files:
        if filename.endswith('.csv'):
            name = filename.removesuffix('.csv')
            dfs[name] = pd.read_csv(
                os.path.join(root, filename),
                parse_dates=['Date'],
                index_col='Date'
            )

# Step 2: find common columns across all CSVs
common_cols = set.intersection(*(set(df.columns) for df in dfs.values()))

# Step 3: plot each common column with one line per CSV
for col in common_cols:
    plt.figure(figsize=(10, 6))
    for label, df in dfs.items():
        plt.plot(df.index, df[col], label=label)
    plt.xlabel('Date')
    plt.ylabel(col)
    plt.title(f'{col} Comparison')
    plt.legend()

    # sanitize filename
    col_sanitized = col.replace('/', '_')
    plt.savefig(os.path.join(figure_path, f'{col_sanitized}.png'))
    plt.close()

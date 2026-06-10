"""
Plots the annual percent change tables produced by compute_annual_pool_change.py,
one figure per chemistry pool variable with one line per watershed, for the
chemistry pool stability analysis (1990-2010).
"""

import pandas as pd
import os
import matplotlib.pyplot as plt

main_folder = 'path/to/Manuscripts/Chemistry Pool Analysis'

df_dict = {}

for root, dirs, files in os.walk(main_folder):
    for file in files:
        if 'annual_change.csv' in file:
            name = file.split('_')[0]+'_'+file.split('_')[1]
            filepath = os.path.join(root, file)
            df = pd.read_csv(filepath, index_col='Year')
            df = df[(df.index >= 1990) & (df.index <= 2010)]
            df_dict[name] = df
            

for title, df in df_dict.items():
    df.index = df.index.astype(int)
    plt.figure(figsize=(10, 6))

    for watershed in df.columns:
        plt.plot(df.index, df[watershed], label=watershed, linewidth=2)

    plt.title(title, fontsize=16)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Percent Change', fontsize=14)
    plt.grid(True, alpha=0.3)
    
    years = sorted(df.index.unique())
    tick_years = list(range(years[0], years[-1] + 1, 2))
    plt.xticks(tick_years)

    # Put the legend outside so many watersheds fit comfortably
    plt.legend(title='Watershed',
               bbox_to_anchor=(1.04, 1),
               loc='upper left')

    plt.tight_layout()
    plt.savefig(os.path.join(main_folder, f'{title}_annual_change.png'))
    plt.close()

import matplotlib.pyplot as plt

for title, df in df_dict.items():

    # Ensure index is integer years
    df.index = df.index.astype(int)

    # Compute the average across columns (axis=1 = across watersheds)
    avg_series = df.mean(axis=1)

    plt.figure(figsize=(10, 6))
    plt.plot(avg_series.index, avg_series.values, linewidth=3)

    plt.title(title, fontsize=16)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Mean Average Percent Change', fontsize=14)
    plt.grid(True, alpha=0.3)

    # Tick marks every 2 years (consistent with your previous plots)
    years = sorted(avg_series.index.unique())
    tick_years = list(range(years[0], years[-1] + 1, 2))
    plt.xticks(tick_years)

    plt.tight_layout()
    plt.savefig(os.path.join(main_folder, f'{title}_average_annual_change.png'))
    plt.close()

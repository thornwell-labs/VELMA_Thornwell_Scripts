"""
Plots observed and simulated runoff together for selected year(s), comparing
multiple simulation scenarios on one chart and labeling each year's NSE.
Multi-scenario variant of nse_visualizer.py.
"""

# This file plots observed and simulated runoff on the same plot for specified year(s) and labels the NSE of each year.

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# User must specify these values
data_files = {"Original": "path/to/VELMA_Watersheds/WS10/Results/OR_BR_ws10_10m_8Aug24/DailyResults.csv", 
              "Doubled field capacity": "path/to/VELMA_Watersheds/WS10/Results/OR_BR_ws10_10m_8Aug24b/DailyResults.csv"}
years = range(1990, 1994)

# This block takes care of title formatting
years_string = ''
for year in years:
    if len(years_string) == 0:
        years_string = f'{year}'
    else:
        years_string = years_string+f', {year}'
    if len(years) >= 5:
        years_string = f'{years[0]} to {years[-1]}'

# Filter the desired years into dataframes
dataframes = {}
for name, path in data_files.items():
    df = pd.read_csv(path)
    df_filtered = df[df['Year'].isin(years)].copy()
    df_filtered['Date'] = pd.to_datetime(df_filtered['Year'].astype(str) +
                                            df_filtered['Day'].astype(str), format='%Y%j')
    dataframes[name] = df_filtered


# This block of code plots the simulated and observed runoff in millimeters
plt.figure(figsize=(10, 6))
for name, df in dataframes.items():
    plt.plot(df['Date'], df['Runoff_All(mm/day)_Delineated_Average'],
            label=f'{name}', linewidth=2, alpha=0.7)
plt.ylabel('Runoff (mm)')
plt.title(f'Runoff for {years_string}')
plt.xlabel('Date')
plt.legend()
plt.grid(True)
plt.show()

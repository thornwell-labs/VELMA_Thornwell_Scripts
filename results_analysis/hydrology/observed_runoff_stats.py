"""
Quick-look statistics for an observed streamflow file: filters to a year
range, prints the mean runoff, and plots the daily series.
"""

import pandas as pd
import matplotlib.pyplot as plt


file_path = ('path/to/VELMA_Watersheds/Elwha/Elwha_Working/'
             'Data_Inputs30m/m_7_Observed/USGS12045500_Elwha_atMcDonald_streamflow_1981_2021_labeled.csv')

df = pd.read_csv(file_path)
years = range(1990, 2020)
df['Year'] = pd.to_datetime(df['Date']).dt.year
df_filtered = df[df['Year'].isin(years)].copy()
runoff = df_filtered['Runoff-mm']
date = df_filtered['Date']
mean_value = df_filtered['Runoff-mm'].mean()
print(f'Mean runoff in mm is {mean_value}')

plt.plot(date, runoff)
plt.xlabel('Date')
plt.xticks(ticks=date[::365])
plt.xticks(rotation=45)
plt.ylabel('Runoff, mm')
plt.show()

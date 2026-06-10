"""
Plots the simulated day-of-year envelope (min/max as dotted lines, mean as a
solid line) for a VELMA variable and overlays observed Ecology monitoring data
as points, producing a figure comparing simulated and observed seasonality.
"""

#  Takes a VELMA results file and an observed data file for a parameter of interest
#  Calculates average, min, and max daily results for each Jday
#  Plots min and max as dotted lines, average as solid line
#  Adds observed data as points on the chart

import pandas as pd
import matplotlib.pyplot as plt
import os

# User inputs
obs_file = r"path\to\VELMA_Watersheds\Puyallup\Data_Inputs30m\m_7_Observed\Ecology_10A070_Puyallup_Temperature,_water_1987-2021.csv"
sim_file = r"path\to\VELMA_Watersheds\Puyallup\Results\MULTI_WA_Puyallup30m_Historical_resampled_3_Penumbra\Results_126201\Cell_i126201_x107_y134_dlnWriter.csv"
obs_start = 1987
parameter = 'Water_Surface_Temperature(degrees_C)'
# 'NH4_Loss(gN/day/m2)_Delineated_Average', 'NO3_Loss(gN/day/m2)_Delineated_Average', 'DOC_Loss(gC/day/m2)_Delineated_Average', 'Runoff_All(mm/day)_Delineated_Average'
# 'Water_Surface_Temperature(degrees_C)'
parameter_label = 'Water Temperature (deg C) at 10A070 in Puyallup watershed'
start_year = 2009
end_year = 2019
out_file = f'path/to/VELMA_Watersheds/Puyallup/Analysis/Puyallup_Temp_10A070_Penumbra.png'

# --------------------------------------------------------------------------------------------------------------------------- #

if 'DailyResults' in sim_file:
    day_column = 'Day'
else:
    day_column = 'Jday'

results_df = pd.read_csv(sim_file, usecols=['Year', day_column, parameter])

# Filter between start_year and end_year
mask = (results_df['Year'] >= start_year) & (results_df['Year'] <= end_year)
subset = results_df.loc[mask]

# Group by Julian day and compute min, mean, max
daily_stats = subset.groupby(day_column)[parameter].agg(
    min = 'min',
    mean = 'mean',
    max = 'max'
).reset_index()

# Load observed data (no header, single column of values)
obs_df = pd.read_csv(obs_file, header=None, names=['Value'])
date_index   = pd.date_range(start=f'{obs_start}-01-01', periods=len(obs_df), freq='D')
obs_df.index = date_index

# Restrict observed data to the same years and compute Jday
obs_period = obs_df[(obs_df.index.year >= start_year) & (obs_df.index.year <= end_year)].copy()
obs_period['Jday'] = obs_period.index.dayofyear

# Make sure the nan values are read correctly
obs_period['Value'] = pd.to_numeric(obs_period['Value'], errors='coerce')

# Plot with min/max dotted and average solid
plt.figure(figsize=(10, 6))
plt.plot(daily_stats[day_column], daily_stats['mean'], label='Model mean', linestyle='-')
plt.plot(daily_stats[day_column], daily_stats['min'],  label='Model min',  linestyle=':')
plt.plot(daily_stats[day_column], daily_stats['max'],  label='Model max',  linestyle=':')

# Add observed data as points
plt.scatter(obs_period['Jday'], obs_period['Value'],
            label='Observed', edgecolor='k', zorder=5)

plt.xlabel('Julian Day')
plt.ylabel(parameter_label)
plt.title(f'Daily {parameter_label} ({start_year}–{end_year})')
plt.legend()
plt.tight_layout()
os.makedirs(os.path.dirname(out_file), exist_ok=True)
plt.savefig(out_file)
plt.show()

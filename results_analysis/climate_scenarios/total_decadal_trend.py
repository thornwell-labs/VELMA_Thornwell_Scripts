"""
Plots the total decadal trend of a variable (e.g. rain) summed across all 20
PSIMF watersheds over the full simulation period, giving a single
region-wide trend line per decade.
"""

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

folder_path = r"path\to\PSIMF Management\Proof_of_Concept_QC\Full_Results\Loads"

out_folder = 'path/to/PSIMF Management/Proof_of_Concept_QC/Decadal_Trend_Analysis'

variable_of_interest = 'Rain(mm_day)_Delineated_Average'
variable_name = 'Rain'

# Create a dataframe and populate it with the total from all 20 watersheds
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if 'SSM_Loads' in file:
            watershed_df = pd.read_csv(os.path.join(folder_path, file), usecols=[variable_of_interest, 'Year', 'Day'])
            watershed_df['Date'] = pd.to_datetime(
                            watershed_df['Year'].astype(str) + watershed_df['Day'].astype(str).str.zfill(3),
                            format='%Y%j',
                            errors='coerce'
                        )
            if file == files[0]:
                full_df = watershed_df
            else:
                full_df[variable_of_interest] = full_df[variable_of_interest] + watershed_df[variable_of_interest]  # This should create values indexed by date if they don't already exist. Otherwise, add the values to the existing values.

# Add the decade and Julian day to the data
full_df["Year"] = full_df["Date"].dt.year
full_df = full_df[full_df["Year"] >= 2010]
full_df["Julian_Day"] = full_df["Date"].dt.dayofyear
full_df["Decade"] = (full_df["Year"] // 10) * 10

# Filter years as desired
year_range = list(range(2020, 2030)) + list(range(2040, 2050))
full_df = full_df[full_df["Year"].isin(year_range)]

# Calculate mean precip by Julian day in each decade
decade_variable = (
    full_df.groupby(["Decade", "Julian_Day"])[variable_of_interest]
    .mean()
    .unstack(level=0))

# Convert to 7-day rolling averages
decade_variable_smooth = decade_variable.rolling(window=7, center=True, min_periods=1).mean()

decade_variable_smooth.to_csv(f'{out_folder}/full_smoothed_{variable_name}_decadal.csv')

# Pick a cool to warm color gradient
decades = sorted(decade_variable_smooth.columns)
colors = plt.cm.plasma(np.linspace(0, 1, len(decades)))

# Plot the smoothed average by Julian day for each decade
plt.figure(figsize=(10, 6))
for decade, color in zip(decades, colors):
    plt.plot(
        decade_variable_smooth.index,
        decade_variable_smooth[decade],
        label=f"{decade}s",
        color=color,
        linewidth=2
    )
plt.xlabel("Julian Day")
plt.ylabel(f"Average {variable_of_interest}")
plt.title(f"Average {variable_of_interest} by Julian Day (7-day Rolling Mean)")
plt.legend(title="Decade", loc="upper right")
plt.tight_layout()
plt.savefig(f'{out_folder}/total_{variable_name}_2020s_vs_2040s.png')
plt.show()

"""
Plots seasonal trends of a variable (e.g. runoff) by decade, summed across all
20 PSIMF watersheds, using day-of-year curves per decade to show seasonal
shifts through the century. See decadal_seasonal_trend_precip.py for the
precipitation-input variant.
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

folder_path = r"path\to\PSIMF Management\Proof_of_Concept_QC\Full_Results\Loads"

out_folder = 'path/to/PSIMF Management/Proof_of_Concept_QC/Decadal_Trend_Analysis'

variable_of_interest = 'Runoff(m3/s)'
variable_name = 'Runoff'

# Create a dataframe and populate it with the total from all 20 watersheds
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if 'SSM_Loads' in file:
            watershed_df = pd.read_csv(os.path.join(folder_path, file), usecols=[variable_of_interest, 'Date'], parse_dates=['Date'])
            if file == files[0]:
                full_df = watershed_df
            else:
                full_df[variable_of_interest] = full_df[variable_of_interest] + watershed_df[variable_of_interest]  # This should create values indexed by date if they don't already exist. Otherwise, add the values to the existing values.

# Add the decade and Julian day to the data
full_df["Year"] = full_df["Date"].dt.year
full_df["Month"] = full_df["Date"].dt.month
full_df = full_df[full_df["Year"] >= 2010]
full_df["Julian_Day"] = full_df["Date"].dt.dayofyear
full_df["Decade"] = (full_df["Year"] // 10) * 10

# This season definition matches the SPARROW season definition
season_dict = {
    'Spring': range(91, 149+1),  # Spring: April - June
    'Summer': range(150, 257+1),  # Summer: July - September
    'Fall': range(258, 366+1),  # Fall: October - December
    'Winter': range(1, 90+1)  # Winter: January - March
}

def assign_season(jday):
    for season, days in season_dict.items():
        if jday in days:
            return season

# Create a 'Season' column based on the SPARROW seasonal definition
full_df['Season'] = full_df['Julian_Day'].apply(assign_season)

# Filter years as desired
year_range = list(range(2020, 2030)) + list(range(2040, 2050))
full_df = full_df[full_df["Year"].isin(year_range)]


# Sum within each year-season
seasonal_totals = (
    full_df.groupby(["Year", "Decade", "Season"])[variable_of_interest]
    .sum()
    .reset_index()
)


# Calculate seasonal means in each decade
decade_variable = (
    full_df.groupby(["Decade", "Season"])[variable_of_interest]
    .mean()
    .unstack(level=0))

# Add percent difference column
decade_variable["Percent Difference"] = (
    (decade_variable[2040] - decade_variable[2020]) / decade_variable[2020])*100
decade_variable.to_csv(f'{out_folder}/{variable_name}_decadal_by_month.csv')

# Bar chart of percent difference by season
plt.figure(figsize=(8, 5))
decade_variable["Percent Difference"].plot(kind="bar", color="steelblue", edgecolor="black")
plt.axhline(0, color="black", linewidth=1)
ax = decade_variable["Percent Difference"].plot(kind="bar", color="steelblue", edgecolor="black")
ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.0f}%"))
plt.ylabel("Percent Difference")
plt.xlabel("Season")
plt.title(f"{variable_name} Percent Difference by Season: 2040s vs 2020s")
plt.tight_layout()
plt.savefig(f"{out_folder}/{variable_name}_percent_difference_by_season.png", dpi=300)
plt.show()

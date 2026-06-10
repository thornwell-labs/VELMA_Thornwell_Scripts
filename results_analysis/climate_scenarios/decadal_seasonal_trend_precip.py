"""
Plots seasonal trends of precipitation inputs (e.g. rain) by decade, summed
across the PSIMF watersheds from the full hydro results files. Precipitation
variant of decadal_seasonal_trend.py.
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

folder_path = r"path\to\PSIMF Management\Proof_of_Concept_QC\Full_Results"

out_folder = 'path/to/PSIMF Management/Proof_of_Concept_QC/Decadal_Trend_Analysis'

variable_of_interest = 'Rain(mm_day)_Delineated_Average'
variable_name = 'Rain'

full_df = None

# Create a dataframe and populate it with the total from all 20 watersheds
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if 'full_hydro_results' in file:
            watershed_df = pd.read_csv(os.path.join(folder_path, file), usecols=[variable_of_interest, 'Year', 'Day'])
            watershed_df['Date'] = pd.to_datetime(
                            watershed_df['Year'].astype(str) + watershed_df['Day'].astype(str).str.zfill(3),
                            format='%Y%j',
                            errors='coerce'
                        )
            if full_df is None:
                full_df = watershed_df
            else:
                full_df[variable_of_interest] = full_df[variable_of_interest] + watershed_df[variable_of_interest]  # This should create values indexed by date if they don't already exist. Otherwise, add the values to the existing values.

# Add the decade and Julian day to the data
full_df["Year"] = full_df["Date"].dt.year
full_df["Month"] = full_df["Date"].dt.month
full_df = full_df[full_df["Year"] >= 2010]
full_df["Julian_Day"] = full_df["Date"].dt.dayofyear
full_df["Decade"] = (full_df["Year"] // 10) * 10

# # This season definition matches the SPARROW season definition
# season_dict = {
#     'Spring': range(91, 149+1),  # Spring: April - June
#     'Summer': range(150, 257+1),  # Summer: July - September
#     'Fall': range(258, 366+1),  # Fall: October - December
#     'Winter': range(1, 90+1)  # Winter: January - March
# }

# def assign_season(jday):
#     for season, days in season_dict.items():
#         if jday in days:
#             return season

# # Create a 'Season' column based on the SPARROW seasonal definition
# full_df['Season'] = full_df['Julian_Day'].apply(assign_season)

# Filter years as desired
# year_range = list(range(2020, 2030)) + list(range(2040, 2050))
year_range = list(range(2020, 2030)) + list(range(2040, 2050))
full_df = full_df[full_df["Year"].isin(year_range)]


# Sum within each year-month
seasonal_totals = (
    full_df.groupby(["Year", "Decade", "Month"])[variable_of_interest]
    .sum()
    .reset_index()
)

# seasonal_totals.to_csv(f'{out_folder}/{variable_name}_by_month.csv')

# # Loop over each month and plot the variable vs year, with chart title labeled by month
# months = list(range(1, 13))
# month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
# for month, month_name in zip(months, month_names):
#     seasonal_totals_plot = seasonal_totals[seasonal_totals['Month'] == month]
#     plt.figure(figsize=(8, 5))
#     plt.plot(seasonal_totals_plot['Year'], seasonal_totals_plot[variable_of_interest])
    
#     # Trendline
#     x = seasonal_totals_plot['Year'].to_numpy()
#     y = seasonal_totals_plot[variable_of_interest].to_numpy()
#     slope, intercept = np.polyfit(x, y, 1)
#     x_line = np.linspace(x.min(), x.max(), 100)
#     y_line = slope * x_line + intercept
#     plt.plot(x_line, y_line, color='red', linestyle='--', linewidth=1, label='Linear trend')
    
#     plt.ylabel(f"{variable_name}")
#     plt.xlabel("Year")
#     plt.title(f"{variable_name} in {month_name}")
#     plt.tight_layout()
#     plt.savefig(f"{out_folder}/{variable_name}_yearly_change_in_{month_name}_to_2050.png", dpi=300)
#     plt.close()


# Average those monthly totals across each decade
decade_variable = (
    seasonal_totals.groupby(["Decade", "Month"])[variable_of_interest]
    .mean()
    .unstack(level=0)
)


# Calculate seasonal means in each decade
# decade_variable = (
#     full_df.groupby(["Decade", "Month"])[variable_of_interest]
#     .mean()
#     .unstack(level=0))

# Add percent difference column
decade_variable["Percent Difference"] = (
    (decade_variable[2040] - decade_variable[2020]) / decade_variable[2020])*100
# decade_variable.to_csv(f'{out_folder}/{variable_name}_decadal_by_month.csv')

# Bar chart of percent difference by month
plt.figure(figsize=(8, 5))
decade_variable["Percent Difference"].plot(kind="bar", color="steelblue", edgecolor="black")
plt.axhline(0, color="black", linewidth=1)
ax = decade_variable["Percent Difference"].plot(kind="bar", color="steelblue", edgecolor="black")
ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.0f}%"))
plt.ylabel("Percent Difference")
plt.xlabel("Month")
plt.title(f"{variable_name} Percent Difference by Month: 2040s vs 2020s")
plt.tight_layout()
plt.savefig(f"{out_folder}/{variable_name}_percent_difference_by_month_2040_vs_2020.png", dpi=300)
plt.show()

"""
Plots century-scale trends of hydrologic variables (rain, snowmelt, soil
saturation, ET, air temperature, runoff) summed across the PSIMF watersheds
from the full hydro results files. See the _monthly_average variant for
monthly aggregation.
"""

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

folder_path = 'path/to/PSIMF Management/Proof_of_Concept_QC/Full_Results'
out_folder = 'path/to/PSIMF Management/Proof_of_Concept_QC/Hydro_Analysis'

variables_of_interest = {'Rainfall_mm': 'Rain(mm_day)_Delineated_Average',
                         'Snow Melt_mm': 'Snow_Melt(mm_day)_Delineated_Average',
                         'Soil Saturation_frac': 'Soil_Saturation_Fraction_Delineated_Average_Layer_1',
                         'Evapotranspiration_mm': 'ET(mm_day)_Delineated_Average',
                         'Air Temp_degC': 'Air_Temperature(degC)_Delineated_Average',
                         'Runoff_mm': 'Runoff_All(mm_day)_Delineated_Average'
                         }

full_df = None

# Create a dataframe and populate it with the total runoff from all 20 watersheds
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if "full_hydro_results" in file:
            watershed_df = pd.read_csv(os.path.join(folder_path, file), usecols=['Year', 'Day'] + list(variables_of_interest.values()))
            watershed_df['Date'] = pd.to_datetime(watershed_df['Year'], format='%Y') + pd.to_timedelta(watershed_df['Day'] - 1, unit='D')
            watershed_df = watershed_df.set_index('Date').drop(columns=['Year', 'Day'])
            if full_df is None:
                full_df = watershed_df
            else:
                full_df = full_df.add(watershed_df, fill_value=0)

full_df = full_df.reset_index()
# Add the decade and Julian day to the data
full_df["Year"] = full_df["Date"].dt.year
full_df = full_df[full_df["Year"] >= 2010]
full_df["Julian_Day"] = full_df["Date"].dt.dayofyear
full_df["Decade"] = (full_df["Year"] // 10) * 10

# Filter years as desired
year_range = list(range(2010, 2050))
full_df = full_df[full_df["Year"].isin(year_range)]

# Calculate mean by Julian day in each decade
for name, variable in variables_of_interest.items():
    variable_df = (
        full_df.groupby(["Decade", "Julian_Day"])[variable]
        .mean()
        .unstack(level=0))

    # Convert to 7-day rolling averages
    decade_variable_smooth = variable_df.rolling(window=7, center=True, min_periods=1).mean()

    decade_variable_smooth.to_csv(f'{out_folder}/total_smoothed_{name}_decadal.csv')

    # Pick a cool to warm color gradient
    decades = sorted(decade_variable_smooth.columns)
    colors = plt.cm.plasma(np.linspace(0, 1, len(decades)))

    # Plot the smoothed average runoff by Julian day for each decade
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
    plt.ylabel(f"Average {name}")
    plt.title(f"Average {name} by Julian Day (7-day Rolling Mean)")
    plt.legend(title="Decade", loc="upper right")
    plt.tight_layout()
    plt.savefig(f'{out_folder}/total_{name}_by_decade.png')
    plt.show()

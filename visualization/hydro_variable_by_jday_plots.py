"""
Plots each hydrologic variable in a watershed's compiled full-period results by
day of year, with one line per decade and optional seasonal divider lines, to
visualize how the seasonal cycle of each variable shifts across decades.
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

watershed = 'Big Beef'
full_results_file_path = 'path/to/VELMA_Watersheds/Big_Beef/Results/Big_Beef_PSIMF_full_hydro_results.csv'
out_folder = 'path/to/VELMA_Watersheds/Big_Beef/Analysis/Big_Beef_PSIMF_Hydro_by_Jday'
seasonal_lines = True
show_plot = False

# Define which days the seasonal lines will plot on if the seasonal_lines flag is True
seasonal_line_days = [1, 91, 150, 258]

# Create out_folder if it doesn't already exist
os.makedirs(out_folder, exist_ok=True)

# Read in the results
full_df = pd.read_csv(full_results_file_path)

# Will want to plot every column other than Year and Day
variables_of_interest = list(full_df.columns)
for c in ['Year', 'Day']:
    variables_of_interest.remove(c)
variable_names = [v.replace('_Delineated_Average', '') for v in variables_of_interest]

# Add the decade to the data
full_df["Decade"] = (full_df["Year"] // 10) * 10

# Filter years as desired
year_range = list(range(2010, 2020)) + list(range(2040, 2050))
full_df = full_df[full_df["Year"].isin(year_range)]


for variable, name in zip(variables_of_interest, variable_names):
    # Calculate mean by Julian day in each decade
    decade_runoff = (
        full_df.groupby(["Decade", "Day"])[variable]
        .mean()
        .unstack(level=0))

    # Convert to 7-day rolling averages
    decade_runoff_smooth = decade_runoff.rolling(window=7, center=True, min_periods=1).mean()

    # Pick a cool to warm color gradient
    decades = sorted(decade_runoff_smooth.columns)
    colors = plt.cm.plasma(np.linspace(0, 1, len(decades)))

    # Plot the smoothed average by Julian day for each decade
    plt.figure(figsize=(10, 6))
    for decade, color in zip(decades, colors):
        plt.plot(
            decade_runoff_smooth.index,
            decade_runoff_smooth[decade],
            label=f"{decade}s",
            color=color,
            linewidth=2
        )
        
    # Add seasonal vertical lines if requested
    if seasonal_lines:
        for d in seasonal_line_days:
            plt.axvline(
                x=d,
                color='gray',
                linestyle='--',
                linewidth=1,
                alpha=0.7
            )
        season_labels = ["Winter", "Spring", "Summer", "Fall"]
        season_centers = [46, 121, 204, 312]  # midpoints of the seasonal ranges
        for label, x in zip(season_labels, season_centers):
            plt.text(
                x,
                0.98, # near the top of the axes
                label,
                ha='center',
                va='top',
                transform=plt.gca().get_xaxis_transform(),
                fontsize=10,
                color='gray'
            )
            
    plt.xlabel("Julian Day")
    plt.ylabel(f"{name}")
    plt.title(f"Average {name} in {watershed} by Julian Day (7-day Rolling Mean)")
    plt.legend(title="Decade", loc="upper right")
    plt.tight_layout()
    plt.savefig(f'{out_folder}/{watershed}_total_{name}_by_decade.png')
    if show_plot == True:
        plt.show()

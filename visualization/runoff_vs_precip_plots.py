"""
Plots day-of-year runoff by decade alongside average precipitation for one
watershed, combining the decadal PSIMF result folders with the precipitation
driver series to show how the runoff seasonal cycle shifts relative to
precipitation. Companion to precip_vs_runoff_charts.py.
"""

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

watershed_name = 'Nooksack'
out_folder = 'path/to/PSIMF Management/Proof_of_Concept_QC/Figures/Nooksack'
precip_file = "path/to/VELMA_Watersheds/Nooksack/Data_Inputs30m/m_2_Weather/2_SpatialModel/Nooksack_Historic1987_2005_Future2006_2099/Average_Precip_ByDate.csv"
root = 'path/to/PSIMF Management/Proof_of_Concept_QC/'
runoff_folders = [root+'2019_Results',
                  root+'2029_Results',
                  root+'2039_Results',
                  root+'2049_Results',
                  root+'2059_Results',
                  root+'2069_Results',
                  root+'2079_Results',
                  root+'2089_Results',
                  root+'2099_Results'
]

precip_df = pd.read_csv(precip_file, parse_dates=["Date"])

# Add the decade and Julian day to the precip data
precip_df["Year"] = precip_df["Date"].dt.year
precip_df = precip_df[precip_df["Year"] >= 2010]
precip_df["Julian_Day"] = precip_df["Date"].dt.dayofyear
precip_df["Decade"] = (precip_df["Year"] // 10) * 10

# Calculate mean precip by Julian day in each decade
decade_precip = (
    precip_df.groupby(["Decade", "Julian_Day"])["Precip_avg"]
    .mean()
    .unstack(level=0))

runoff_dfs = []
# Walk through the runoff results and collect the watershed results
for folder in runoff_folders:
    decade = os.path.basename(folder).split("_")[0]
    all_files = [f for f in os.listdir(folder) if watershed_name in f and f.endswith(".csv")]

    for f in all_files:
        fpath = os.path.join(folder, f)
        df = pd.read_csv(fpath, parse_dates=["Date"])
        df["Year"] = df["Date"].dt.year
        df = df[df["Year"] >= 2010]  # Exclude pre-2010
        df["Julian_Day"] = df["Date"].dt.dayofyear
        df["Decade"] = (df["Year"] // 10) * 10
        runoff_dfs.append(df[["Decade", "Julian_Day", "Runoff(m3/s)"]])

    # Calculate the mean runoff for each Julian day in each decade
    runoff_all = pd.concat(runoff_dfs)
    decade_runoff = (
        runoff_all.groupby(["Decade", "Julian_Day"])["Runoff(m3/s)"]
        .mean()
        .unstack(level=0))
    

# Convert precip and runoff to 7-day rolling averages
window = 7
decade_runoff_smooth = decade_runoff.rolling(window, center=True, min_periods=1).mean()
decade_precip_smooth = decade_precip.rolling(window, center=True, min_periods=1).mean()

# Pick a cool to warm color gradient
decades = sorted(decade_runoff_smooth.columns)
colors = plt.cm.plasma(np.linspace(0, 1, len(decades)))

# Plot the smoothed average runoff by Julian day for each decade
plt.figure(figsize=(10, 6))
for decade, color in zip(decades, colors):
    plt.plot(
        decade_runoff_smooth.index,
        decade_runoff_smooth[decade],
        label=f"{decade}s",
        color=color,
        linewidth=2
    )
plt.xlabel("Julian Day")
plt.ylabel("Average Runoff (m³/s)")
plt.title("Average Runoff by Julian Day (7-day Rolling Mean)")
plt.legend(title="Decade", loc="upper right")
plt.tight_layout()
# plt.show()
plt.savefig(f'{out_folder}/runoff_by_decade.png')

# Plot the smoothed average precipitation by Julian day for each decade
plt.figure(figsize=(10, 6))
for decade, color in zip(decades, colors):
    if decade in decade_precip_smooth.columns:
        plt.plot(
            decade_precip_smooth.index,
            decade_precip_smooth[decade],
            label=f"{decade}s",
            color=color,
            linewidth=2
        )
plt.xlabel("Julian Day")
plt.ylabel("Average Precipitation (mm/day)")
plt.title("Smoothed Average Precipitation by Julian Day (7-day Rolling Mean)")
plt.legend(title="Decade", loc="upper right")
plt.tight_layout()
# plt.show()
plt.savefig(f'{out_folder}/precip_by_decade.png')

# Pairwise runoff–precip plots with shared axis limits
common_decades = sorted(set(decade_runoff_smooth.columns).intersection(decade_precip_smooth.columns))

# Compute shared axis limits
x_min, x_max = decade_runoff_smooth.index.min(), decade_runoff_smooth.index.max()
runoff_min = decade_runoff_smooth.min().min()
runoff_max = decade_runoff_smooth.max().max()
precip_min = decade_precip_smooth.min().min()
precip_max = decade_precip_smooth.max().max()

for decade, color in zip(common_decades, colors):
    runoff = decade_runoff_smooth[decade]
    precip = decade_precip_smooth[decade]

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()

    # Plot smoothed runoff and precip with consistent axes
    ax1.plot(runoff.index, runoff.values, color=color, label="Runoff", linewidth=2)
    ax2.plot(precip.index, precip.values, color=color, alpha=0.4, linestyle="--", label="Precip")

    # Lock axis limits across decades
    ax1.set_xlim(x_min, x_max)
    ax1.set_ylim(runoff_min, runoff_max)
    ax2.set_ylim(precip_min, precip_max)

    ax1.set_xlabel("Julian Day")
    ax1.set_ylabel("Runoff (m³/s)")
    ax2.set_ylabel("Precipitation (mm/day)")
    plt.title(f"Runoff vs Precipitation — {decade}s (7-day Rolling Mean)")
    plt.legend(loc="upper right")
    fig.tight_layout()
    
    # Save figure for each decade
    plt.savefig(f"{out_folder}/{decade}_precip_runoff.png")
    plt.close(fig)

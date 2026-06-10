"""
Computes and plots the distribution of land cover or soil type classes within
a delineated watershed from an .asc grid, as a pie/histogram, with optional
export of the class proportions to CSV.
"""

import numpy as np
import pandas as pd
import rasterio
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap

data_path = 'path/to/VELMA_Watersheds/Cedar/Data_Inputs30m/resampled/asc/Stillaguamish_9soiltypes_resampled_3.asc'
title = '90m Soil Distribution in Cedar watershed'
flag = 'land cover'  # specify 'land cover' or 'soil type' for plot_pie_histogram function
hist_to_csv = True
out_csv_path = 'path/to/VELMA_Watersheds/Cedar/Analysis/Stillaguamish_90m_soil_hist.csv'
delineated_file = 'path/to/VELMA_Watersheds/Stillaguamish/Data_Inputs30m/resampled/asc/Stillaguamish30m_DredgeMask_EEX_resampled_3_delineated.asc'

with rasterio.open(delineated_file) as src:
    data = src.read(1)
    mask = data > 0
    mask = mask.flatten()

with rasterio.open(data_path) as src:
    data = src.read(1)
    profile = src.profile
    transform = src.transform
    nodata_val = src.nodata

# Helper function to compute histogram for land cover distribution
def compute_histogram(data, mask):
    flat = data.flatten()
    valid = flat[mask]
    total = len(valid)
    counts = Counter(valid)
    return {k: v / total * 100 for k, v in counts.items()}

hist = compute_histogram(data, mask)
if hist_to_csv:
    df = pd.DataFrame(list(hist.items()), columns=["Age", "Percent"])
    df.to_csv(out_csv_path, index=False)

# Map the land cover ID's to descriptive names
landcover_names = {
    5: "Alder, 5%",
    6: "Alder, 17%",
    7: "Alder, 37%",
    8: "Alder, 62%",
    9: "Alder, 88%",
    11: "Water",
    12: "Snow/Ice",
    21: "Developed: Open Space",
    22: "Developed: Low Intensity",
    23: "Developed: Medium Intensity",
    24: "Developed: High Intensity",
    31: "Bare Land",
    42: "Evergreen Forest",
    43: "Mixed Forest",
    52: "Shrub / Scrub",
    71: "Grassland",
    81: "Pasture",
    82: "Cultivated",
    90: "Wetlands"
}

# Do the same for soil types
soil_names = {
    12: 'Medium, C/N=12',
    17: 'Medium, C/N=17',
    24: 'Medium, C/N=24',
    112: 'Deep, C/N=12',
    117: 'Deep, C/N=17',
    124: 'Deep, C/N=24',
    212: 'Shallow, C/N=12',
    217: 'Shallow, C/N=17',
    224: 'Shallow, C/N=24'
}

def plot_pie_histogram(hist):
    fig, ax = plt.subplots(figsize=(12, 8))
    if flag == 'land cover':
        all_lc_types = sorted(hist.keys())
        num_types = len(all_lc_types)

        cmap = get_cmap('tab20', num_types)
        color_map = {lc: cmap(i) for i, lc in enumerate(all_lc_types)}
        full_hist = {lc: hist.get(lc, 0.0) for lc in all_lc_types}

        labels = [landcover_names.get(lc, f"Class {lc}") for lc in all_lc_types]
        sizes = list(full_hist.values())
        colors = [color_map[lc] for lc in all_lc_types]
        legend_title = 'Land Cover Types'

    if flag == 'soil type':
        all_soil_types = sorted(hist.keys())
        num_types = len(all_soil_types)

        cmap = get_cmap('tab20', num_types)
        color_map = {lc: cmap(i) for i, lc in enumerate(all_soil_types)}
        full_hist = {lc: hist.get(lc, 0.0) for lc in all_soil_types}

        labels = [soil_names.get(soil, f"Class {soil}") for soil in all_soil_types]
        sizes = list(full_hist.values())
        colors = [color_map[soil] for soil in all_soil_types]
        legend_title = 'Soil Types'

    wedges, _, autotexts = ax.pie(
        sizes,
        colors=colors,
        autopct=lambda p: f'{p:.1f}%' if p >= 1 else '',
        startangle=90,
        pctdistance=0.75,
    )
    ax.legend(
        wedges, labels,
        title=legend_title,
        loc="center left",
        bbox_to_anchor=(0.9, 0, 0.5, 1)  # move closer to chart using these parameters
    )
        
    ax.axis('equal')
    ax.set_title(title, pad=15)  # adjust title position here
    plt.tight_layout()
    plt.show()
    
def plot_bar_histogram(hist):
    plt.hist(hist, bins=20, edgecolor="black")
    plt.xlabel("Age")
    plt.ylabel("Count")
    plt.title("Age Distribution")
    plt.show()


plot_pie_histogram(hist)
# plot_bar_histogram(hist)

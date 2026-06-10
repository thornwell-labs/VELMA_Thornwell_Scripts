"""
Compares VELMA-simulated total nitrogen loads against SPARROW model
predictions for the PSIMF watersheds, computing percent differences and
producing comparison plots.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import glob
import os

# Define the list of the 24 PSIMF watersheds
watersheds = [
    "Hoko", "Elwha", "Dungeness", "Big_Beef", "Huge", "Samish", "Nisqually",
    "Green", "Skokomish", "Nooksack", "Puyallup", "Mercer",
    "Issaquah", "Juanita", "Quilcene", "Duckabush", 
    "Deschutes", "Stillaguamish", "Snohomish", "Skagit"
]

SPARROW_folder = 'path/to/SPARROW/predict_puget_tn'
VELMA_folder = f'{SPARROW_folder}/VELMA'
percent_diff_list = []

for watershed in watersheds:
    # Find SPARROW file that contains the watershed name (case insensitive match)
    sparrow_files = glob.glob(f"{SPARROW_folder}/*{watershed}*.csv")
    if not sparrow_files:
        print(f"SPARROW file not found for {watershed}")
        percent_diff_list.append(np.nan)
        continue
    
    sparrow_file = sparrow_files[0]  # Use the first match
    sparrow_df = pd.read_csv(sparrow_file)
    
    if 'PLOAD_TOTAL_ND' not in sparrow_df.columns:
        print(f"Missing 'PLOAD_TOTAL_ND' in {sparrow_file}")
        percent_diff_list.append(np.nan)
        continue

    sparrow_tn = sparrow_df['PLOAD_TOTAL_ND']

    # Load corresponding VELMA data
    velma_file = f'{VELMA_folder}/{watershed}_seasonal_nitrogen_load.csv'
    if not os.path.exists(velma_file):
        print(f"VELMA file not found for {watershed}")
        percent_diff_list.append(np.nan)
        continue

    velma_df = pd.read_csv(velma_file)
    
    if 'Nitrogen_Load_kg' not in velma_df.columns:
        print(f"Missing 'Nitrogen_Load_kg' in {velma_file}")
        percent_diff_list.append(np.nan)
        continue

    velma_tn = velma_df['Nitrogen_Load_kg']

    if len(sparrow_df) != len(velma_df):
        print(f'ERROR: Length mismatch for {watershed}. SPARROW={len(sparrow_df)}, VELMA={len(velma_df)}')
        percent_diff_list.append(np.nan)
    else:
        percent_diff = (np.sum(sparrow_tn) - np.sum(velma_tn)) / np.sum(sparrow_tn)
        print(f'Percent difference for {watershed}: {percent_diff:.2%}')
        percent_diff_list.append(percent_diff)

        # Plotting with curved (smoothed) lines
        plt.figure(figsize=(10, 5))

        try:
            # Convert period to numeric
            x = pd.to_numeric(sparrow_df['period'], errors='coerce')
            mask = ~np.isnan(x) & ~np.isnan(sparrow_tn) & ~np.isnan(velma_tn)
            x = x[mask]
            sparrow_y = sparrow_tn[mask]
            velma_y = velma_tn[mask]

            # Create smooth x range and interpolated curves
            if len(x) >= 4:  # make_interp_spline needs at least k+1 points (k=3 for cubic)
                x_smooth = np.linspace(x.min(), x.max(), 300)
                sparrow_smooth = make_interp_spline(x, sparrow_y, k=3)(x_smooth)
                velma_smooth = make_interp_spline(x, velma_y, k=3)(x_smooth)

                plt.plot(x_smooth, sparrow_smooth, label='SPARROW TN Load', linewidth=2)
                plt.plot(x_smooth, velma_smooth, label='VELMA TN Load', linewidth=2)
            else:
                # Fallback to original straight-line plot if not enough points
                plt.plot(x, sparrow_y, label='SPARROW TN Load', linewidth=2)
                plt.plot(x, velma_y, label='VELMA TN Load', linewidth=2)

            plt.title(f'Nitrogen Load Comparison: {watershed}')
            plt.xlabel('Period')
            plt.ylabel('Nitrogen Load (kg)')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()

            plot_path = os.path.join(VELMA_folder, f"{watershed}_TN_comparison_plot.png")
            plt.savefig(plot_path)
            plt.close()

        except Exception as e:
            print(f"Plotting error for {watershed}: {e}")
            percent_diff_list[-1] = np.nan  # overwrite last entry with NaN due to failure

# Save percent difference summary
percent_diff_df = pd.DataFrame({'Watershed': watersheds, 'Percent Diff TN (SPARROW - VELMA)': percent_diff_list})
percent_diff_df.to_csv(f'{VELMA_folder}/percent_diff_by_watershed.csv', index=False)

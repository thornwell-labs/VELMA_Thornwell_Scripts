"""
Runs a seasonal hydrologic analysis for a single watershed using daily (not
seasonally summed) values, assigning days to seasons and producing correlation
plots/heatmaps between hydrologic variables. Single-watershed,
non-summed variant of seasonal_hydrologic_analysis.py.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr
from sklearn.preprocessing import StandardScaler
import seaborn as sns
import os

watershed = 'Big Beef'
hydro_results_file = 'path/to/VELMA_Watersheds/Big_Beef/Results/Big_Beef_PSIMF_full_hydro_results.csv'
out_path = 'path/to/VELMA_Watersheds/Big_Beef/Analysis/Hydro_by_Season_No_Sum/'
show_plots = False

# Create output directory if it doesn't exist
os.makedirs(out_path, exist_ok=True)

# This season definition matches the SPARROW season definition
# Reconsider this seasonal definition to match the days in the transpiration limiter function
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

# Read in the results data
daily_combined = pd.read_csv(hydro_results_file)

# Filter to only data from 2010-2049 for mid-century paper
daily_combined = daily_combined[daily_combined['Year'] >= 2010]
daily_combined = daily_combined[daily_combined['Year'] < 2050]

# Create a 'Season' column based on the SPARROW seasonal definition
daily_combined['Season'] = daily_combined['Day'].apply(assign_season)

# Write hydrologic results by season
output_path = f'{out_path}{watershed}_PSIMF_Hydrology_by_Season.csv'
daily_combined.to_csv(output_path, float_format='%.4f', index=False)

# Shorter column names
daily_combined.columns = daily_combined.columns.str.replace('_Delineated_Average', '', regex=False)

# Define dependent and independent variables
dependent_var = 'Runoff_All(mm_day)'
independent_vars = ['Snow_Melt(mm_day)', 'Rain(mm_day)', 'Soil_Saturation_Fraction_Layer_1', 'ET(mm_day)']


# Create regression plots and perform Pearson correlation analysis
for season in season_dict.keys():
    # Filter to season
    season_df = daily_combined[daily_combined['Season'] == season]
    
    # Scale all variables (including dependent) to zero mean, unit variance
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(season_df[independent_vars + [dependent_var]])

    # Create a DataFrame from scaled data
    scaled_df = pd.DataFrame(scaled_data, columns=independent_vars + [dependent_var], index=season_df.index)

    # Perform Pearson and Spearman correlation and save results
    rows = []
    print(f"Pearson and Spearman correlations during {season} with Runoff_Change_mm (scaled):")
    for var in independent_vars:
        pearson_corr, pearson_p = pearsonr(scaled_df[dependent_var], scaled_df[var])
        spearman_corr, spearman_p = spearmanr(scaled_df[dependent_var], scaled_df[var])
        print(f"{var}: Pearson r = {pearson_corr:.2f} (p={pearson_p:.3f}), Spearman rho = {spearman_corr:.2f} (p={spearman_p:.2f})")
        row = var, pearson_corr, pearson_p, spearman_corr, spearman_p
        rows.append(row)

    pearson_spearman_df = pd.DataFrame(rows, columns=['Variable', 'Pearson R', 'Pearson p', 'Spearman R', 'Spearman p'])
    pearson_spearman_df.to_csv(f'{out_path}{season}_Correlation_to_Runoff_Analysis.csv', index=False)

    # Use the original (unscaled) data for scatter plots to keep units interpretable
    df = season_df.copy()  # original data (non-scaled)

    # Scatter plots with regression lines
    plt.figure(figsize=(16, 10))
    for i, var in enumerate(independent_vars, 1):
        plt.subplot(2, 3, i)
        sns.regplot(x=var, y=dependent_var, data=df, scatter_kws={'s':30, 'alpha':0.7}, line_kws={'color':'red'}, ci=None)
        plt.xlabel(var)
        plt.ylabel(dependent_var)
        plt.title(f'{dependent_var} vs {var} in {season}')
    plt.tight_layout()
    plt.savefig(f'{out_path}{watershed}_{season}_Hydro_Regression_Charts.png')
    if show_plots == True:
        plt.show()

    # Correlation heatmap (Pearson)
    vars_for_corr = [dependent_var] + independent_vars
    n = len(vars_for_corr)

    # Initialize matrices
    r_mat = pd.DataFrame(np.zeros((n, n)), index=vars_for_corr, columns=vars_for_corr)
    p_mat = pd.DataFrame(np.ones((n, n)), index=vars_for_corr, columns=vars_for_corr)

    # Compute r and p
    for i in vars_for_corr:
        for j in vars_for_corr:
            r, p = pearsonr(scaled_df[i], scaled_df[j])
            r_mat.loc[i, j] = r
            p_mat.loc[i, j] = p

    # Mask non-significant correlations
    mask = (p_mat >= 0.05) | np.triu(np.ones_like(r_mat, dtype=bool))

    # Create annotation matrix with significance stars
    annot = r_mat.copy().astype(str)

    for i in vars_for_corr:
        for j in vars_for_corr:
            p = p_mat.loc[i, j]
            r = r_mat.loc[i, j]

            if p < 0.001:
                annot.loc[i, j] = f"{r:.2f}***"
            elif p < 0.01:
                annot.loc[i, j] = f"{r:.2f}**"
            elif p < 0.05:
                annot.loc[i, j] = f"{r:.2f}*"
            else:
                annot.loc[i, j] = ""

    # Plot heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        r_mat,
        mask=mask,
        annot=annot,
        fmt="",
        cmap="coolwarm",
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.5,
        cbar_kws={'label': 'Pearson r'}
    )

    plt.title(f'{season} Pearson Correlation Matrix in {watershed}\n(* p<0.05, ** p<0.01, *** p<0.001)', fontsize=16)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(rotation=0, fontsize=10)

    plt.tight_layout()
    plt.savefig(f'{out_path}{watershed}_{season}_Hydro_Pearson_Correlation_Matrix_.png')
    if show_plots == True:
        plt.show()
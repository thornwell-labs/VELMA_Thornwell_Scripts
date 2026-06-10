"""
Correlates hydrologic variables with land cover change for one watershed.
Joins the PSIMF hydrologic-change table with LCCM developed-cover proportions
(relative to the 2011 baseline) and computes Pearson/Spearman correlations
plus a heatmap. Single-watershed companion to
annual_change_hydrologic_correlation_analysis.py.
"""

import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

# File paths
results_data_path = "path/to/VELMA_Watersheds/Nisqually/Analysis/PSIMF_Hydrologic_Change_Nisqually.csv"
lccm_data_path = "path/to/PSIMF Management/LCCM_QC/Nisqually_land_cover_proportions.csv"
out_analysis_path = 'path/to/VELMA_Watersheds/Nisqually/Analysis/'

# Load LCCM data with Year as index
lccm_df = pd.read_csv(lccm_data_path, index_col='Year')

# Calculate change in developed cover since baseline (2011)
baseline = lccm_df.loc[2011, 'Percent_Developed']
lccm_df['Delta_Percent_Developed'] = lccm_df['Percent_Developed'] - baseline

# Load analysis data with Year as index
analysis_df = pd.read_csv(results_data_path, index_col='Year')

# Join Delta_Percent_Developed from LCCM data into analysis dataframe
analysis_df = analysis_df.join(lccm_df['Delta_Percent_Developed'], how='inner')

# Drop rows with missing data to ensure clean correlation calculations
analysis_df_clean = analysis_df.dropna()

# Identify dependent and independent variables
dependent_var = 'Runoff_Change_mm'
independent_vars = [col for col in analysis_df.columns if col != dependent_var]

# Scale all variables (including dependent) to zero mean, unit variance
scaler = StandardScaler()
scaled_data = scaler.fit_transform(analysis_df[independent_vars + [dependent_var]])

# Create a DataFrame from scaled data
scaled_df = pd.DataFrame(scaled_data, columns=independent_vars + [dependent_var], index=analysis_df.index)


rows = []
print("Pearson and Spearman correlations with Runoff_Change_mm (scaled):")
for var in independent_vars:
    pearson_corr, pearson_p = pearsonr(scaled_df[dependent_var], scaled_df[var])
    spearman_corr, spearman_p = spearmanr(scaled_df[dependent_var], scaled_df[var])
    print(f"{var}: Pearson r = {pearson_corr:.3f} (p={pearson_p:.3f}), Spearman rho = {spearman_corr:.3f} (p={spearman_p:.3f})")
    row = var, pearson_corr, pearson_p, spearman_corr, spearman_p
    rows.append(rows)

pearson_spearman_df = pd.DataFrame(rows, columns=['Variable', 'Pearson R', 'Pearson p', 'Spearman R', 'Spearman p'])
pearson_spearman_df.to_csv(f'{out_analysis_path}Correlation_to_Runoff_Analysis.csv')

# Use the original (unscaled) data for scatter plots to keep units interpretable
df = analysis_df.copy()  # original data (non-scaled)

dependent_var = 'Runoff_Change_mm'
variables = [col for col in df.columns if col != dependent_var]

# Scatter plots with regression lines
plt.figure(figsize=(16, 10))
for i, var in enumerate(variables, 1):
    plt.subplot(2, 3, i)
    sns.regplot(x=var, y=dependent_var, data=df, scatter_kws={'s':30, 'alpha':0.7}, line_kws={'color':'red'}, ci=None)
    plt.xlabel(var)
    plt.ylabel(dependent_var)
    plt.title(f'{dependent_var} vs {var}')
plt.tight_layout()
plt.savefig(f'{out_analysis_path}Hydro_Regression_Charts.png')
plt.show()

# Correlation heatmap (Pearson)
corr = df[[dependent_var] + variables].corr()
plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, fmt=".2f")

plt.title('Pearson Correlation Matrix', fontsize=16)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.yticks(rotation=0, fontsize=10)

plt.tight_layout()
plt.savefig(f'{out_analysis_path}Hydro_Pearson_Correlation_Matrix.png')
plt.show()

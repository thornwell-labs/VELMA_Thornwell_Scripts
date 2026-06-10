"""
Processes USFS Forest Inventory and Analysis (FIA) data into per-plot
aboveground carbon estimates. Computes carbon per acre from tree-level carbon
and trees-per-acre, and writes a simplified per-plot table. Includes
commented-out code for the prior tree-to-plot merge step.
"""

import pandas as pd

# plot_path = 'path/to/FIA_Plot_Data/WA_PLOT_PSIMF.csv'
# tree_path = 'path/to/FIA_Plot_Data/WA_TREE.csv'
# merged_path = 'path/to/FIA_Plot_Data/WA_TREE_PLOT_PSIMF.csv'

# # Read plot and tree data
# plot_df = pd.read_csv(plot_path)  # Already filtered to relevant plots
# tree_df = pd.read_csv(tree_path, low_memory=False)

# # Merge tree data with plot data, keeping only matching rows
# merged_df = tree_df.merge(plot_df, left_on="PLT_CN", right_on="CN", how="inner")

# # Save the merged data to a new CSV
# merged_df.to_csv(merged_path, index=False)

# print(f"Filtered tree data saved with {len(merged_df)} rows.")


merged_path = 'path/to/FIA_Plot_Data/WA_TREE_PLOT_PSIMF.csv'
output_path = 'path/to/FIA_Plot_Data/WA_Carbon_Per_Plot_PSIMF.csv'

df = pd.read_csv(merged_path)

# Step 1: Compute the adjusted carbon value
df['Carbon_lb_acre'] = df['CARBON_AG'] * df['TPA_UNADJ']

filtered_df = df[['PLT_CN', 'TREE', 'LAT', 'LON', 'ELEV', 'MEASYEAR', 'CARBON_AG', 'TPA_UNADJ']]
filtered_df.to_csv('path/to/FIA_Plot_Data/WA_TREE_PLOT_PSIMF_Simplified.csv', index=False)

# Step 2: Sum adjusted carbon values for each plot
carbon_per_plot = df.groupby(['PLT_CN', 'MEASYEAR'], as_index=False)['Carbon_lb_acre'].sum()

# Step 3: Convert from lb/acre to grams/m²
carbon_per_plot['Carbon_g_m2'] = round(carbon_per_plot['Carbon_lb_acre'] * 0.112084,0)

# Step 4: Extract unique plot information
plot_info = df[['PLT_CN', 'LAT', 'LON', 'ELEV', 'MEASYEAR']].drop_duplicates(subset=['PLT_CN', 'MEASYEAR'])

carbon_per_plot = carbon_per_plot.merge(plot_info, on=['PLT_CN', 'MEASYEAR'], how='left')

# Save the result
carbon_per_plot.to_csv(output_path, index=False)
print(f"Processed carbon data saved to {output_path}")

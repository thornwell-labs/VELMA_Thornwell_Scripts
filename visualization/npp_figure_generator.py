"""
Plots annual net primary productivity (NPP) by land cover group from a VELMA
AnnualResults file, grouping cover types into forested, developed, water, and
cultivated categories. See visualize_total_npp.py for the watershed-total
version.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

annual_results_file_path = 'path/to/VELMA_Watersheds/Skokomish/Results/MULTI_WA_Skokomish30m_9Jun2025_Hyak/Results_1365037/AnnualResults.csv'
output_dir = 'path/to/VELMA_Watersheds/Skokomish/Analysis/9June'

# ----------------------------------------------------------------------------------------

cover_types_dict = {
    'Forested Cover Types': ['Alder37Percent_7', 'Alder17Percent_6', 'Alder5Percent_5',
                             'Alder88Percent_9', 'Alder62Percent_8', 'MixedForest_43',
                             'EvergreenForest_42', 'Wetlands_90', 'ShrubScrub_52'],
    'Developed Cover Types': ['DevelopedMediumIntensity_23', 'DevelopedOpenSpace_21',
                              'DevelopedLowIntensity_22', 'DevelopedHighIntensity_24',
                              'BareLand_31'],
    'Water Cover Types': ['SnowIce_12', 'Water_11'],
    'Cultivated Cover Types': ['Grassland_71', 'Pasture_81', 'Cultivated_82'],
}

df = pd.read_csv(annual_results_file_path)

# Filter for ANNUAL_SUM rows
df = df[df['Annual_Result'] == 'ANNUAL_SUM']

# Keep only 'Year' and NPP cover columns
npp_columns = [col for col in df.columns if 'NPP_C(gC/day/m2)_Cover_Average' in col]
columns_to_keep = ['Year'] + npp_columns
df = df[columns_to_keep]

# === PLOT ===
os.makedirs(output_dir, exist_ok=True)
df.to_csv(f'{output_dir}/annual_npp.csv')

for group_name, cover_list in cover_types_dict.items():
    plt.figure(figsize=(10, 6))

    for cover in cover_list:
        col_name = f'{cover}_NPP_C(gC/day/m2)_Cover_Average'
        if col_name in df.columns:
            plt.plot(df['Year'], df[col_name], label=cover)
        else:
            print(f"Warning: Column '{col_name}' not found in data.")

    plt.title(f'Annual Sum NPP by Year: {group_name}')
    plt.xlabel('Year')
    plt.ylabel('NPP (gC/day/m2)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'2_annual_npp_{group_name.replace(" ", "_")}.png'))
    plt.close()

print("Plots saved to:", output_dir)

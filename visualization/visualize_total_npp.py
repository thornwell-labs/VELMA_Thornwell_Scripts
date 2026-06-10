"""
Plots total annual net primary productivity (NPP) summed across cover types
for a watershed from a VELMA daily results file. Watershed-total counterpart
to npp_figure_generator.py.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

results_path = 'path/to/VELMA_Watersheds/Samish/Results/Samish_09Jan2024/DailyResults.csv'
cover_types = ['DevelopedMediumIntensity_23',  'Cultivated_82', 'EvergreenForest_42',
'Alder88Percent_9', 'Grassland_71', 'Pasture_81', 
'SnowIce_12', 'MixedForest_43', 'BareLand_31', 'Water_11']

# 'ScrubShrub_52', 'Wetlands_ 90',  # Keeping these separate because there were none of these type in the outlet watershed of the Samish
# 'Alder62Percent_8', 'Alder37Percent_7', 'Alder17Percent_6', 'Alder5Percent_5', 
# 'DevelopedOpenSpace_21', 'DevelopedLowIntensity_22', 'DevelopedHighIntensity_24',

columns = ['Year']

for cover in cover_types:
    column = f'{cover}_NPP_C(gC/day/m2)_Cover_Average'
    columns.append(column)


df = pd.read_csv(results_path, usecols=columns)

# Create a list of each unique year contained in Year column
years = sorted(df['Year'].unique())

# Sum NPP values for each cover type by year
npp_totals_by_cover = {cover: [] for cover in cover_types}

for year in years:
    year_data = df[df['Year'] == year]
    for cover in cover_types:
        column_name = f'{cover}_NPP_C(gC/day/m2)_Cover_Average'
        npp_totals_by_cover[cover].append(year_data[column_name].sum())
        

# Plot NPP by year for each cover type
plt.figure(figsize=(12, 8))

for cover in cover_types:
    plt.plot(years, npp_totals_by_cover[cover], label=cover)

# Customize the plot
plt.title('Total NPP by Year', fontsize=14)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Total NPP (gC/day/m2)', fontsize=12)
plt.legend(loc='best', fontsize=10, ncol=2)
plt.grid(True)

# Show the plot
plt.tight_layout()
plt.show()

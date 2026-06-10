"""
Plots percent change over time for chemistry pool columns (humus, biomass,
litter, NH4, NO3) in a VELMA DailyResults file, grouped by cover and soil
type. Used to check whether pools are drifting during spin-up runs.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os


# Root file path for DailyResults .csv file and where to save results figures
root_path = 'path/to/VELMA_Watersheds/Samish/Results/MULTI_WA_Samish30m_21Jan2025'

# Path to the DailyResults.csv file
csv_path = f'{root_path}/Results_635473/DailyResults.csv'

# Path to generated figures
figure_path = f'{root_path}/Figures'
if not(os.path.exists(figure_path)):
    os.makedirs(figure_path)

cover_types = ['EvergreenForest_42', 'Alder88Percent_9', 'ShrubScrub_52', 'Grassland_71','Pasture_81', 'Cultivated_82', 'Wetlands_90', 'MixedForest_43',
               'DevelopedMediumIntensity_23', 'DevelopedOpenSpace_21', 'DevelopedLowIntensity_22', 'DevelopedHighIntensity_24', 'Alder62Percent_8',
               'Alder37Percent_7', 'Alder17Percent_6', 'Alder5Percent_5', 'SnowIce_12', 'BareLand_31', 'Water_11']
soil_types = ['Medium_CN24', 'Medium_CN12', 'Medium_CN17']

# Specify column from the DailyResults file (key) and choose simplified label for plotting (value)
columns_of_interest = {}
for soil in soil_types:
    columns_of_interest[f'{soil}_Humus_Pool(gC/m2)_Soil_Average'] = f'{soil}_Humus'
for cover in cover_types:
    columns_of_interest[f'{cover}_Biomass_Pool(gC/m2)_Cover_Average'] = f'{cover}_Biomass'
    columns_of_interest[f'{cover}_agLitter_Pool(gC/m2)_Cover_Average'] = f'{cover}_agLitter'
    columns_of_interest[f'{cover}_bgLitter_Pool(gC/m2)_Cover_Average'] = f'{cover}_bgLitter'
    columns_of_interest[f'{cover}_NH4_Pool(gN/m2)_Cover_Average'] = f'{cover}_NH4'
    columns_of_interest[f'{cover}_NO3_Pool(gN/m2)_Cover_Average'] = f'{cover}_NO3'

# Read the DailyResults csv and filter the columns of interest by which ones are available
with open(csv_path, 'r') as f:
    first_line = f.readline().strip().split(',')
columns_of_interest = {col: name for col, name in columns_of_interest.items() if col in first_line}

# Load the CSV file and set a datetime object as the index
results_df = pd.read_csv(csv_path, usecols=['Year', 'Day'] +list(columns_of_interest.keys()))
results_df['Datetime'] = pd.to_datetime(results_df['Year'].astype(str) + results_df['Day'].astype(str), format='%Y%j')
results_df.set_index('Datetime', inplace=True)

# Calculate % difference from the same day of the previous year
for column, name in columns_of_interest.items():
    results_df[f'Percent_Diff_{name}'] = results_df[column].pct_change(periods=365) * 100

# Extract the year from the index and add it as a column for grouping
results_df['Year'] = results_df.index.year

# Group by year and calculate the average percent difference per year
for column, name in columns_of_interest.items():
    average_percent_diff = results_df.groupby('Year')[f'Percent_Diff_{name}'].mean()
    for year, avg_diff in average_percent_diff.items():
        print(f"Year: {year}, Category: {name}, Average Percent Difference: {avg_diff:.2f}%")

# Plot column of interest by the datetime index
for column, name in columns_of_interest.items():
    plt.figure(figsize=(12, 6))
    plt.plot(results_df.index, results_df[column], label=name, color='blue')
    plt.xlabel('Date')
    plt.ylabel(name)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{figure_path}/Daily_{name}.png')
    plt.close()

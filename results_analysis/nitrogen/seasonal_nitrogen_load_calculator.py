"""
Calculates seasonal total nitrogen loads (NH4+NO3+DON, in kg) from a VELMA
DailyResults file using the SPARROW season definitions, writing one row per
year and season for comparison with SPARROW load estimates.
"""

import pandas as pd

results_folder = r"path\to\VELMA_Watersheds\Stillaguamish\Results\MULTI_WA_Stillaguamish30m_16Jul2025_resampled_3_Hyak\Results_225493"
watershed_area = 90*90*83901 # m^2
watershed_name = 'Stillaguamish'
df = pd.read_csv(f'{results_folder}/DailyResults.csv', usecols=['Year', 'Day', 'Runoff_All(mm/day)_Delineated_Average', 
                                  'NH4_Loss(gN/day/m2)_Delineated_Average', 'NO3_Loss(gN/day/m2)_Delineated_Average', 
                                  'DON_Loss(gN/day/m2)_Delineated_Average'])

# This season definition matches the SPARROW season definition
season_dict = {
    '1': range(91, 181+1),  # Spring: April - June
    '2': range(182, 273+1),  # Summer: July - September
    '3': range(274, 365+1),  # Fall: October - December
    '4': range(1, 90+1)  # Winter: January - March
}

output_rows = []

for year in range(2005, 2020+1):
    yearly_df = df[df['Year'] == year]
    for season, days in season_dict.items():
        seasonal_df = yearly_df[yearly_df['Day'].isin(days)]
        nitrogen_load_kg = 0
        for nitrogen_pool in ['NH4', 'NO3', 'DON']:
            pool_gN_m2 = seasonal_df[f'{nitrogen_pool}_Loss(gN/day/m2)_Delineated_Average'].sum()
            pool_gN = pool_gN_m2*watershed_area
            pool_kgN = pool_gN / 1000
            nitrogen_load_kg += pool_kgN
        output_rows.append({
            'Year': year,
            'Season': season,
            'Nitrogen_Load_kg': nitrogen_load_kg
        })


out_df = pd.DataFrame(output_rows)
out_df.to_csv(f'{results_folder}/{watershed_name}_seasonal_nitrogen_load.csv', index=False)
print(f'Processed seasonal nitrogen loads for {watershed_name}.')

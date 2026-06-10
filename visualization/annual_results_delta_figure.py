"""
Plots annual change (ANNUAL_DELTA) in the major carbon and nitrogen spatial
pools from a VELMA AnnualResults file, producing separate carbon-pool and
nitrogen-pool figures to check pool stability over time.
"""

import pandas as pd
import matplotlib.pyplot as plt

results_folder = 'path/to/VELMA_Watersheds/Deschutes/Results/MULTI_WA_Deschutes30m_9Jul2025_Hyak/Results_127824'
annual_results_df = pd.read_csv(f'{results_folder}/AnnualResults.csv', usecols=['Year', 'Annual_Result', 'Biomass_Pool(gC/m2)_Delineated_Average', 
                                          'Humus_Pool(gC/m2)_Delineated_Average', 'agLitter_Pool(gC/m2)_Delineated_Average', 
                                          'bgLitter_Pool(gC/m2)_Delineated_Average', 'NH4_Pool(gN/m2)_Delineated_Average', 
                                          'NO3_Pool(gN/m2)_Delineated_Average', 'DON_Pool(gN/m2)_Delineated_Average'])

annual_results_df = annual_results_df[annual_results_df['Annual_Result'] == 'ANNUAL_DELTA']
annual_results_df = annual_results_df[annual_results_df['Year'] >= 1990]
annual_results_df = annual_results_df.set_index('Year')

plt.figure(figsize=(10,6))
for column in ['Biomass_Pool(gC/m2)_Delineated_Average', 
                'Humus_Pool(gC/m2)_Delineated_Average', 'agLitter_Pool(gC/m2)_Delineated_Average', 
                'bgLitter_Pool(gC/m2)_Delineated_Average']:
    plt.plot(annual_results_df[column], label=column)
plt.xlabel('Year')
plt.ylabel('Annual Change (gC/m2)')
plt.title('Annual Change in Major Carbon Spatial Pools')
plt.legend()
plt.tight_layout()
plt.savefig(f'{results_folder}/annual_carbon_changes.png')
plt.show()
plt.close()

plt.figure(figsize=(10,6))
for column in ['NH4_Pool(gN/m2)_Delineated_Average', 'NO3_Pool(gN/m2)_Delineated_Average', 'DON_Pool(gN/m2)_Delineated_Average']:
    plt.plot(annual_results_df[column], label=column)
plt.xlabel('Year')
plt.ylabel('Annual Change (gN/m2)')
plt.title('Annual Change in Major Nitrogen Spatial Pools')
plt.legend()
plt.tight_layout()
plt.savefig(f'{results_folder}/annual_nitrogen_changes.png')
plt.show()
plt.close()
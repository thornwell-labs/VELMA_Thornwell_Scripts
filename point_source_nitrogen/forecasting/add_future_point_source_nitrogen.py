"""
Adds projected point-source nitrogen loads (hatcheries, WWTPs) to VELMA daily
result nitrogen losses for a future-scenario run. Looks up facility IDs by
name, normalizes each facility's monthly loads by watershed area, and adds
them to the NH4/NO3/DON loss columns of DailyResults.csv.
"""

import pandas as pd
import os

# Define all of these
results_folder ='path/to/VELMA_Watersheds/Nisqually/Results/MULTI_WA_Nisqually30m_PSIMF_17July2025_resampled_3_Hyak/Results_161002'
cell_area = 90*90
outlet_id = 161002
facility_names = ['Skookum Creek Hatchery', 'Kendall Creek Hatchery']
point_source_folder = 'path/to/VELMA_Tools/Point_Source_Data'

# ---------------------------------------------------------------- #

facility_csv = os.path.join(point_source_folder, 'fac_attributes (1).csv')

# Read facility ID mapping
facility_df = pd.read_csv(facility_csv, usecols=['FAC_ID', 'FAC_NAME'], dtype='str')

fac_id_list = []
for name in facility_names:
    match = facility_df[facility_df['FAC_NAME'].str.lower() == name.lower()]
    if not match.empty:
        fac_id = match.iloc[0]['FAC_ID']
        fac_id_list.append(fac_id)
    else:
        print(f'WARNING: {name} not found in facility attributes spreadsheet')

# Calculate watershed area from the ReachSummary.csv file
watershed_area_df = pd.read_csv(f'{results_folder}/ReachSummary.csv', usecols=['iOutlet', 'Reach_plus_Contributor_Cells'], dtype=int)
matches = watershed_area_df.loc[watershed_area_df['iOutlet'] == outlet_id, 'Reach_plus_Contributor_Cells']
if matches.empty:
    raise ValueError(f"Outlet ID {outlet_id} not found in ReachSummary.csv")
elif len(matches) > 1:
    raise ValueError(f"Multiple entries for Reach_ID {outlet_id} found in ReachSummary.csv")
cell_count = matches.values[0]
watershed_area = cell_area * cell_count

# Load VELMA daily results file
velma_parameters = ['NH4_Loss(gN/day/m2)_Delineated_Average','NO3_Loss(gN/day/m2)_Delineated_Average', 'DON_Loss(gN/day/m2)_Delineated_Average']
velma_daily_results = pd.read_csv(f'{results_folder}/DailyResults.csv', 
                                  usecols=['Year', 'Day'] + velma_parameters)

# Add a 'month' column (integer 1 through 12) based on which day of the year it is
velma_daily_results['Month'] = pd.to_datetime(velma_daily_results['Day'], format='%j').dt.month
for fac_id in fac_id_list:
    # Load monthly nitrogen load
    monthly_nitrogen_load = pd.read_csv(f'{point_source_folder}/{fac_id}_monthly_load.csv')
    # Perform conversion to VELMA units
    monthly_nitrogen_load['NH4_LOAD_G_DAY_M2'] = monthly_nitrogen_load['NH4_LOAD_KG_DAY'] * 1000 / watershed_area
    monthly_nitrogen_load['NO3_LOAD_G_DAY_M2'] = monthly_nitrogen_load['NO3_LOAD_KG_DAY'] * 1000 / watershed_area
    monthly_nitrogen_load['DON_LOAD_G_DAY_M2'] = monthly_nitrogen_load['DON_LOAD_KG_DAY'] * 1000 / watershed_area
    
    # Join monthly nitrogen loads to daily data based on month and year
    velma_daily_results = velma_daily_results.merge(
        monthly_nitrogen_load[['YEAR', 'MONTH', 'NH4_LOAD_G_DAY_M2', 'NO3_LOAD_G_DAY_M2', 'DON_LOAD_G_DAY_M2']]
        .rename(columns={'YEAR': 'Year', 'MONTH': 'Month'}),
        on=['Year', 'Month'],
        how='left')

    # Add the loads to VELMA output
    velma_daily_results['NH4_Loss(gN/day/m2)_Delineated_Average'] += velma_daily_results['NH4_LOAD_G_DAY_M2'].fillna(0)
    velma_daily_results['NO3_Loss(gN/day/m2)_Delineated_Average'] += velma_daily_results['NO3_LOAD_G_DAY_M2'].fillna(0)
    velma_daily_results['DON_Loss(gN/day/m2)_Delineated_Average'] += velma_daily_results['DON_LOAD_G_DAY_M2'].fillna(0)

    # Drop load columns to avoid re-adding in the next loop
    velma_daily_results.drop(columns=['NH4_LOAD_G_DAY_M2', 'NO3_LOAD_G_DAY_M2', 'DON_LOAD_G_DAY_M2'], inplace=True)

velma_daily_results.drop(columns=['Month'], inplace=True)
velma_daily_results.to_csv(f'{results_folder}/DailyResults_withPointSource.csv', index=False)

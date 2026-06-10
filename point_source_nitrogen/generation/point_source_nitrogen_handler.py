"""
Orchestrates point-source nitrogen processing for a watershed. Classifies the
named facilities as hatcheries, WWTPs, or industrial sources, calls the
matching generator (wwtp_nitrogen_generator.py / hatchery_nitrogen_generator.py)
to produce monthly load CSVs, and normalizes loads by watershed area for
addition to VELMA results.
"""

import pandas as pd
from wwtp_nitrogen_generator import generate_wwtp_monthly_nitrogen
from hatchery_nitrogen_generator import generate_hatchery_monthly_nitrogen

# Define these
results_folder = 'path/to/VELMA_Watersheds/Skagit/Results/MULTI_WA_Skagit30m_PSIMF_2099_resampled_3/Results_1874413'
cell_area = 90*90
outlet_id = 1874413
facility_names = ['Burlington WWTP', 'Seattle City Light Diablo', 'Marblemount Hatchery', 'Concrete STP', 'WA DFW Barnaby Slough', 'Samish Hatchery', 'Sedro Woolley WWTP']

# ----------------------------------------------------------------------------------------------- #

# Calculate watershed area from the ReachSummary.csv file
watershed_area_df = pd.read_csv(f'{results_folder}/ReachSummary.csv', usecols=['iOutlet', 'Reach_plus_Contributor_Cells'], dtype=int)
matches = watershed_area_df.loc[watershed_area_df['iOutlet'] == outlet_id, 'Reach_plus_Contributor_Cells']
if matches.empty:
    raise ValueError(f"Outlet ID {outlet_id} not found in ReachSummary.csv")
elif len(matches) > 1:
    raise ValueError(f"Multiple entries for Reach_ID {outlet_id} found in ReachSummary.csv")
cell_count = matches.values[0]
watershed_area = cell_area * cell_count

# Look up the facility ID's and type of facilities
point_source_folder = 'path/to/VELMA_Tools/Point_Source_Data'
facility_csv = f'{point_source_folder}/fac_attributes (1).csv'
facility_df = pd.read_csv(facility_csv, usecols=['FAC_ID', 'FAC_NAME', 'FAC_TYPE'], dtype='str')

hatchery_fac_id = []
wwtp_fac_id = []
industrial_fac_id = []

for name in facility_names:
    match = facility_df[facility_df['FAC_NAME'].str.lower() == name.lower()]
    if not match.empty:
        fac_id = match.iloc[0]['FAC_ID']
        fac_type = match.iloc[0]['FAC_TYPE']
        if fac_type == 'sic_0921':
            hatchery_fac_id.append(fac_id)
        elif fac_type == 'sic_4952':
            wwtp_fac_id.append(fac_id)
        elif fac_type == 'sic_INDU':
            industrial_fac_id.append(fac_id)
    else:
         print(f'WARNING: {name} not found in facility attributes spreadsheet')   

# Generate monthly nitrogen load csv files by facility ID
# if hatchery_fac_id:
#     generate_hatchery_monthly_nitrogen(hatchery_fac_id)

# if industrial_fac_id:
#     generate_hatchery_monthly_nitrogen(industrial_fac_id)

# if wwtp_fac_id:
#     generate_wwtp_monthly_nitrogen(wwtp_fac_id)

# Combine all facility IDs
fac_id_list = hatchery_fac_id + industrial_fac_id + wwtp_fac_id

# Load VELMA daily results file
velma_parameters = ['NH4_Loss(gN/day/m2)_Delineated_Average','NO3_Loss(gN/day/m2)_Delineated_Average', 'DON_Loss(gN/day/m2)_Delineated_Average']
velma_daily_results = pd.read_csv(f'{results_folder}/DailyResults.csv', 
                                  usecols=['Year', 'Day', 'Runoff_All(mm/day)_Delineated_Average', 'DOC_Loss(gC/day/m2)_Delineated_Average'] + velma_parameters)

# Filter velma_daily_results by year to only include results from years 2005 to 2020
# velma_daily_results = velma_daily_results[velma_daily_results['Year'].between(2005, 2020)]

# Add a 'month' column (integer 1 through 12) based on which day of the year it is
velma_daily_results['Month'] = pd.to_datetime(velma_daily_results['Day'], format='%j').dt.month

for fac_id in fac_id_list:
    # Load monthly nitrogen load
    monthly_nitrogen_load = pd.read_csv(f'{point_source_folder}/{fac_id}_monthly_load.csv')
    # Perform conversion to VELMA units
    monthly_nitrogen_load['NH4_LOAD_G_DAY_M2'] = monthly_nitrogen_load['NH4_LOAD_KG_DAY'] * 1000 / watershed_area
    monthly_nitrogen_load['NO3_LOAD_G_DAY_M2'] = monthly_nitrogen_load['NO3_LOAD_KG_DAY'] * 1000 / watershed_area
    monthly_nitrogen_load['DON_LOAD_G_DAY_M2'] = monthly_nitrogen_load['DON_LOAD_KG_DAY'] * 1000 / watershed_area
    
    # Join monthly nitrogen loads to daily data based on month
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

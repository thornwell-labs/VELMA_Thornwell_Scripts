"""
Compiles VELMA results into inputs for the WASP water quality model. Maps
VELMA outlet cells to NHD COMIDs, determines each outlet's contributing
reaches from ReachSummary.csv, and exports per-COMID flow and nitrogen time
series for the WASP team.
"""

import pandas as pd
import os

# Establish these directories and the cell size
results_folder = 'path/to/VELMA_Watersheds/Snohomish/Results/MULTI_WA_Snohomish_30m_3Jul2025_WASP_resampled_3_Hyak'
cell_area = 90*90 # m^2
velma_comid_link = 'path/to/VELMA_Watersheds/Snohomish/Analysis/SnohomishWASPModelCOMIDs.csv'

# Read the VELMA/COMID link and create lists of outlets and COMIDs
velma_comid_df = pd.read_csv(velma_comid_link, dtype=int)
outlet_list = velma_comid_df['90m VELMA cell index'].tolist()
comid_list = velma_comid_df['COMIDs Used'].tolist()


# This block determines the contributing ID's of each outlet
first_outlet = outlet_list[0]
folder = f'{results_folder}/Results_{str(first_outlet)}'

# Read in ReachSummary with padded columns
with open(f'{folder}/ReachSummary.csv', encoding="utf-8") as f:
    first_line = f.readline().strip().split(",")
    max_cols = max(len(line.strip().split(",")) for line in f)
header = first_line + [f"extra_col{i+1}" for i in range(max_cols - len(first_line))]
contributing_id_df = pd.read_csv(f'{folder}/ReachSummary.csv', header=None, names=header, engine='python')
contributing_id_df = contributing_id_df.iloc[1:].reset_index(drop=True)

# Create column with a list of contributing reach ID's
extra_cols = contributing_id_df.columns[6:]
contributing_id_df['Contributing IDs'] = (
contributing_id_df[extra_cols]        # select extra columns
.replace('', pd.NA)                   # treat empty strings as NA
.stack()                              # stack all non-NA values into one Series per row (this turns values to float)
.astype(int).astype(str)              # switch to string
.groupby(level=0)                     # group by original row index
.agg(','.join)                        # join values with commas
)

# Drop the extra columns
columns_to_keep = ['Reach_ID', 'iOutlet', 'Contributing IDs']
contributing_id_df = contributing_id_df[columns_to_keep]
total_outlet_list = contributing_id_df['iOutlet'].tolist()

# Count number of contributors for each ID
ids = contributing_id_df['Contributing IDs'].fillna('')
contributing_id_df['Number Contributors'] = ids.str.count(',') + (ids != '').astype(int)

# Sort by number of contributors
contributing_id_df = contributing_id_df.sort_values(by='Number Contributors', ascending=True).reset_index(drop=True)
sorted_outlet_list = contributing_id_df['iOutlet'].astype(int).tolist()

# Sort the outlet list and comid list by the same order
outlet_to_comid = dict(zip(outlet_list, comid_list))
outlet_list = sorted_outlet_list
comid_list = [outlet_to_comid.get(o, None) for o in outlet_list]


# This loop processes results for each VELMA outlet and writes it to csv, labeled by reach ID
for outlet in total_outlet_list:
    outlet = int(outlet)
    folder = f'{results_folder}/Results_{str(outlet)}'
    
    # Determine catchment area by reading the reach summary and finding cell count for this outlet
    reach_summary_df = pd.read_csv(f'{folder}/ReachSummary.csv', usecols=['Reach_ID', 'iOutlet', 'Reach_plus_Contributor_Cells'], dtype='int')
    reach = int(reach_summary_df.loc[reach_summary_df['iOutlet'] == outlet, 'Reach_ID'].values[0])
    cell_count = int(reach_summary_df.loc[reach_summary_df['iOutlet'] == outlet, 'Reach_plus_Contributor_Cells'].values[0])
    watershed_area = cell_area * cell_count
    
    # Read the daily results file and index by date
    daily_result_df = pd.read_csv(f'{folder}/DailyResults.csv', 
                                  usecols=['Year', 'Day', 'Runoff_All(mm/day)_Delineated_Average', 'NO3_Loss(gN/day/m2)_Delineated_Average',
                                           'DON_Loss(gN/day/m2)_Delineated_Average', 'NH4_Loss(gN/day/m2)_Delineated_Average',
                                           'DOC_Loss(gC/day/m2)_Delineated_Average'])
    daily_result_df['Date'] = pd.to_datetime(daily_result_df['Year'].astype(str) + daily_result_df['Day'].astype(str), format='%Y%j')
    daily_result_df.set_index('Date', inplace=True)
    
    # Find and read the cell data writer results file for temperature, and index by date
    for filename in os.listdir(folder):
        if 'dlnWriter.csv' in filename:
            cell_data_file = filename
            break
    cell_data_df = pd.read_csv(f'{folder}/{cell_data_file}', usecols=['Year', 'Jday', 'Water_Surface_Temperature(degrees_C)'])
    cell_data_df['Date'] = pd.to_datetime(cell_data_df['Year'].astype(str) + cell_data_df['Jday'].astype(str), format='%Y%j')
    cell_data_df.set_index('Date', inplace=True)
    
    # Join temperature data to the rest of the results
    results_df = pd.concat([daily_result_df, cell_data_df], axis=1)
    
    # Multiply by watershed area to find load
    results_df['Daily_Runoff_cms'] = results_df['Runoff_All(mm/day)_Delineated_Average'] / 1000 * watershed_area / 24 / 60 / 60
    results_df['NO3_gN/s'] = results_df['NO3_Loss(gN/day/m2)_Delineated_Average'] * watershed_area / 24 / 60 / 60
    results_df['DON_gN/s'] = results_df['DON_Loss(gN/day/m2)_Delineated_Average'] * watershed_area / 24 / 60 / 60
    results_df['NH4_gN/s'] = results_df['NH4_Loss(gN/day/m2)_Delineated_Average'] * watershed_area / 24 / 60 / 60
    results_df['DOC_gN/s'] = results_df['DOC_Loss(gC/day/m2)_Delineated_Average'] * watershed_area / 24 / 60 / 60
    results_df['Water_Temp_deg_C'] = results_df['Water_Surface_Temperature(degrees_C)']
    
    out_df = results_df[['Daily_Runoff_cms', 'NO3_gN/s', 'DON_gN/s', 'NH4_gN/s', 'DOC_gN/s', 'Water_Temp_deg_C']]
    out_df.to_csv(f'{results_folder}/total_data_reach_{reach}.csv')
    print(f'Wrote total data file for outlet {outlet}')

print(f'Finished writing total data files. Creating WASP additive data files.')

# This block subtracts runoff and loads from contributing ID's and generates WASP data labeled by COMID
already_subtracted = set()
for outlet, comid in zip(outlet_list, comid_list):
    outlet = str(outlet)
    reach = contributing_id_df.loc[contributing_id_df['iOutlet']==outlet, 'Reach_ID'].values[0]
    results_df = pd.read_csv(f'{results_folder}/total_data_reach_{reach}.csv', index_col='Date')
    contributing_ids_str = contributing_id_df.loc[contributing_id_df['iOutlet']==outlet, 'Contributing IDs'].values[0]
    
    if pd.isna(contributing_ids_str) or contributing_ids_str == '':
        contributing_reach_list = []
    else:
        contributing_reach_list = [int(r) for r in contributing_ids_str.split(',')]
    
    if contributing_reach_list:
        for contributor in contributing_reach_list:
            if contributor in already_subtracted:
                continue
            contributor_df = pd.read_csv(f'{results_folder}/total_data_reach_{contributor}.csv', index_col='Date')
            columns_to_subtract = ['Daily_Runoff_cms', 'NO3_gN/s', 'DON_gN/s', 'NH4_gN/s', 'DOC_gN/s']
            results_df[columns_to_subtract] = results_df[columns_to_subtract].subtract(contributor_df[columns_to_subtract], fill_value=0)
            already_subtracted.add(contributor)

    # Convert units
    out_df = pd.DataFrame(index=results_df.index)
    out_df['Daily_Runoff_cms'] = results_df['Daily_Runoff_cms']
    out_df['Water_Temp_deg_C'] = results_df['Water_Temp_deg_C']
    out_df['NO3_mg/L'] = results_df['NO3_gN/s'] / results_df['Daily_Runoff_cms']
    out_df['DON_mg/L'] = results_df['DON_gN/s'] / results_df['Daily_Runoff_cms']
    out_df['NH4_mg/L'] = results_df['NH4_gN/s'] / results_df['Daily_Runoff_cms']
    out_df['DOC_mg/L'] = results_df['DOC_gN/s'] / results_df['Daily_Runoff_cms']

    # If COMID is not None, write to csv
    if comid:
        out_df.to_csv(f'{results_folder}/wasp_data_COMID_{comid}.csv')
        print(f'Processed WASP data for outlet {outlet}.')
print('Finished processing.')

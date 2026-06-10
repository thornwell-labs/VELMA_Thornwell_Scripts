"""
Calculates the average monthly total nitrogen load for each facility in the
PSIMF point-source facilities list and appends it to the facility attributes
table. Feeds tn_contributor_bar_chart.py.
"""
import pandas as pd
import numpy as np

working_directory = 'path/to/VELMA_Tools/Point_Source_Data'
facility_csv = f'{working_directory}/fac_attributes_PSIMF.csv'
nutrient_load_csv = f'{working_directory}/nutrient_loads (1).csv'
out_facility_csv = f'{working_directory}/PSIMF_fac_monthly_tn.csv'

facility_df = pd.read_csv(facility_csv)
nutrient_load_df = pd.read_csv(nutrient_load_csv, usecols=['FAC_ID', 'TN_LOAD_KG_MO'])

# Initialize empty column
facility_df['AVG_TN_LOAD_KG_MO'] = np.nan

for idx, fac_id in enumerate(facility_df['FAC_ID']):
    # Filter nutrient load records matching this facility ID
    matching_loads = nutrient_load_df[nutrient_load_df['FAC_ID'] == fac_id]['TN_LOAD_KG_MO']
    
    # Calculate the average TN load if there are matches
    if not matching_loads.empty:
        average_monthly_tn = matching_loads.mean()
    else:
        average_monthly_tn = np.nan
    
    # Assign the average to the appropriate row in facility_df
    facility_df.at[idx, 'AVG_TN_LOAD_KG_MO'] = average_monthly_tn

facility_df.to_csv(out_facility_csv, index=False)
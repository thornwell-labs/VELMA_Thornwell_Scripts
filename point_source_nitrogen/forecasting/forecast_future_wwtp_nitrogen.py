"""
Projects wastewater treatment plant nitrogen loads to 2099 using a
county-level population growth rate. Averages each facility's 2010-2020
monthly NH4/NO3/DON loads, then compounds them annually by the growth rate
and appends the projections to the historical monthly load CSVs.
"""

import pandas as pd
import os

county = 'Whatcom'
growth_rate = 1.00989860849807
facility_id_list = ['WA0020435', 'WA0022454', 'WA0022578']  # Whatcom
# facility_id_list = ['WA0020486', 'WA0023302']  # Snohomish
# facility_id_list = ['WA0020150', 'WA0020851', 'WA0023752']  # Skagit
# facility_id_list = ['WA0037231', 'WA0023361', 'WA0020834', 'WA0020303', 'WA0040479', 'WA0023353', 'WA0023281']  # Pierce
# facility_id_list = ['WA0020575', 'WA0029513', 'WA0032182', 'WA0029351', 'WA0022403']  # King
point_source_folder = 'path/to/VELMA_Tools/Point_Source_Data'


for fac_id in facility_id_list:
    monthly_load_path = os.path.join(point_source_folder, f'{fac_id}_monthly_load.csv')
    monthly_load_df = pd.read_csv(monthly_load_path)
    # Filter data for 2010-2020
    filtered_df = monthly_load_df[(monthly_load_df['YEAR'] >= 2010) & (monthly_load_df['YEAR'] <= 2020)]

    # Compute monthly averages
    avg_monthly = filtered_df.groupby('MONTH')[['NH4_LOAD_KG_DAY', 'NO3_LOAD_KG_DAY', 'DON_LOAD_KG_DAY']].mean()
    
    # Project monthly values into the future to 2099
    projections = []
    for year in range(2021, 2100):
        factor = growth_rate ** (year - 2020)
        for month in range(1, 13):
            projected = {
                'YEAR': year,
                'MONTH': month,
                'NH4_LOAD_KG_DAY': avg_monthly.loc[month, 'NH4_LOAD_KG_DAY'] * factor,
                'NO3_LOAD_KG_DAY': avg_monthly.loc[month, 'NO3_LOAD_KG_DAY'] * factor,
                'DON_LOAD_KG_DAY': avg_monthly.loc[month, 'DON_LOAD_KG_DAY'] * factor
            }
            projections.append(projected)

    projections_df = pd.DataFrame(projections)

    # Round projections to the hundredths
    for col in ['NH4_LOAD_KG_DAY', 'NO3_LOAD_KG_DAY', 'DON_LOAD_KG_DAY']:
        projections_df[col] = projections_df[col].round(2)
    
    # Reorder and match original columns
    projections_df = projections_df[['YEAR', 'MONTH', 'NH4_LOAD_KG_DAY', 'NO3_LOAD_KG_DAY', 'DON_LOAD_KG_DAY']]

    # Append to original DataFrame
    combined_df = pd.concat([filtered_df[['YEAR', 'MONTH', 'NH4_LOAD_KG_DAY', 'NO3_LOAD_KG_DAY', 'DON_LOAD_KG_DAY']], projections_df], ignore_index=True)

    # Save combined data back to the original file (overwrite)
    monthly_load_path = os.path.join(point_source_folder, f'{fac_id}_monthly_load.csv')
    combined_df.to_csv(monthly_load_path, index=False)
    print(f'Forecasted data appended to {monthly_load_path}')
    
"""
Generates monthly nitrogen load CSVs (NH4, NO3, DON in kg/day) for fish
hatchery facilities from the Washington Ecology nutrient loads dataset.
Speciates total nitrogen using assumed hatchery fractions (20% NH4, 5% NO3,
75% DON). Called by point_source_nitrogen_handler.py.
"""

import pandas as pd
import numpy as np

def generate_hatchery_monthly_nitrogen(fac_id_list):
    for fac_id in fac_id_list:
        nitrogen_load_csv = 'path/to/VELMA_Tools/Point_Source_Data/nutrient_loads (1).csv'
        output_csv = f'path/to/VELMA_Tools/Point_Source_Data/{fac_id}_monthly_load.csv'

        df = pd.read_csv(nitrogen_load_csv, usecols=['FAC_ID', 'YEAR', 'MONTH', 'TN_LOAD_KG_MO'])
        filtered_df = df[df['FAC_ID'] == fac_id].copy()

        days_in_month = {
            1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
        }

        # Make sure all the columns except the facility ID are numeric
        cols_to_convert = filtered_df.columns.difference(['FAC_ID'])
        filtered_df[cols_to_convert] = filtered_df[cols_to_convert].apply(pd.to_numeric, errors='coerce')


        filtered_df['DAYS'] = filtered_df['MONTH'].map(days_in_month)

        # Assume nitrogen speciation in hatcheries is mostly DON and more ammonia than NO3
        # Assumed percentages: 20% NH4, 5% NO3, 75% DON
        filtered_df['NH4_LOAD_KG_DAY'] = filtered_df['TN_LOAD_KG_MO'] * 0.20 / filtered_df['DAYS']
        filtered_df['NO3_LOAD_KG_DAY'] = filtered_df['TN_LOAD_KG_MO'] * 0.05 / filtered_df['DAYS']
        filtered_df['DON_LOAD_KG_DAY'] = filtered_df['TN_LOAD_KG_MO'] * 0.75 / filtered_df['DAYS']


        # Simplify the result df for exporting
        result = filtered_df[['YEAR', 'MONTH', 'NH4_LOAD_KG_DAY', 'NO3_LOAD_KG_DAY', 'DON_LOAD_KG_DAY']].copy()
        for column in ['NH4_LOAD_KG_DAY', 'NO3_LOAD_KG_DAY', 'DON_LOAD_KG_DAY']:
            result[column] = np.round(result[column], 2)
        result.to_csv(output_csv, index=False)


        # Check the result file for missing data and missing rows
        if len(result) == 192:
            data_flag = False
        else:
            data_flag = True
        if filtered_df.isna().any().any():
            data_flag = True

        if data_flag:
            print(f'Results contained {len(result)} rows. Suspect missing data in {fac_id}.')
        else:
            print(f'Results contained {len(result)} rows and contains valid data in {fac_id}.')

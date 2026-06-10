"""
Generates monthly nitrogen load CSVs (NH4, NO3, DON in kg/day) for wastewater
treatment plants from the Washington Ecology nutrient loads dataset. Speciates
total nitrogen using each facility's reported NH4/NO2+NO3/TKN concentrations,
correcting rows where NH4 exceeds TKN. Called by point_source_nitrogen_handler.py.
"""

import pandas as pd
import numpy as np

def generate_wwtp_monthly_nitrogen(fac_id_list):
    for fac_id in fac_id_list:
        nitrogen_load_csv = 'path/to/VELMA_Tools/Point_Source_Data/nutrient_loads (1).csv'
        output_csv = f'path/to/VELMA_Tools/Point_Source_Data/{fac_id}_monthly_load.csv'

        df = pd.read_csv(nitrogen_load_csv, usecols=['FAC_ID', 'YEAR', 'MONTH', 'TN_LOAD_KG_MO', 'NH4N_MG_L', 'NO2NO3N_MG_L', 'TKN_MG_L', 'TN_MG_L'])
        filtered_df = df[df['FAC_ID'] == fac_id].copy()

        days_in_month = {
            1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
        }
        filtered_df['DAYS'] = filtered_df['MONTH'].map(days_in_month)

        # Make sure all the columns except the facility ID are numeric
        cols_to_convert = filtered_df.columns.difference(['FAC_ID'])
        filtered_df[cols_to_convert] = filtered_df[cols_to_convert].apply(pd.to_numeric, errors='coerce')

        # Calculate monthly loads in units of kg/day
        filtered_df['NH4_LOAD_KG_DAY'] = (filtered_df['NH4N_MG_L'] / filtered_df['TN_MG_L']) * filtered_df['TN_LOAD_KG_MO'] / filtered_df['DAYS']
        filtered_df['NO3_LOAD_KG_DAY'] = (filtered_df['NO2NO3N_MG_L'] / filtered_df['TN_MG_L']) * filtered_df['TN_LOAD_KG_MO'] / filtered_df['DAYS']
        don_ratio = (filtered_df['TKN_MG_L'] - filtered_df['NH4N_MG_L']) / filtered_df['TN_MG_L']
        filtered_df['DON_LOAD_KG_DAY'] = don_ratio * filtered_df['TN_LOAD_KG_MO'] / filtered_df['DAYS']

        # Sometimes NH4 > TKN, resulting in negative DON. This is probably faulty data.
        # In these cases, let's assume NH4 is 50% of TKN and re-calculate NH4 and DON accordingly.
        problem_rows = filtered_df['NH4N_MG_L'] > filtered_df['TKN_MG_L']
        filtered_df.loc[problem_rows, 'NH4N_MG_L'] = 0.5 * filtered_df.loc[problem_rows, 'TKN_MG_L']
        filtered_df.loc[problem_rows, 'NH4_LOAD_KG_DAY'] = (filtered_df.loc[problem_rows, 'NH4N_MG_L'] / filtered_df.loc[problem_rows, 'TN_MG_L']) * filtered_df.loc[problem_rows, 'TN_LOAD_KG_MO'] / filtered_df.loc[problem_rows, 'DAYS']
        filtered_df.loc[problem_rows, 'DON_LOAD_KG_DAY'] = (filtered_df.loc[problem_rows, 'TKN_MG_L'] - filtered_df.loc[problem_rows, 'NH4N_MG_L']) / filtered_df.loc[problem_rows, 'TN_MG_L'] * filtered_df.loc[problem_rows, 'TN_LOAD_KG_MO'] / filtered_df.loc[problem_rows, 'DAYS']


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


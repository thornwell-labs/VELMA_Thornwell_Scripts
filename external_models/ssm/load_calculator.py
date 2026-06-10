"""
Converts SSM-format concentration outputs (mg/L) to loads (kg/day) using each
watershed's runoff, and computes flow-weighted temperature contributions.
Writes SSM_Loads files for the PSIMF full-results set.
"""

import os
import pandas as pd

columns_to_convert = ['NH4_Loss(mg/L)', 'NO3_Loss(mg/L)', 'DON_Loss(mg/L)', 'DOC_Loss(mg/L)']
temperature_col = 'Water_Surface_Temperature(degrees_C)'

input_folder = r"path\to\PSIMF Management\Proof_of_Concept_QC\Full_Results"
output_folder = r"path\to\PSIMF Management\Proof_of_Concept_QC\Full_Results\Loads"

total_runoff_file = r"path\to\PSIMF Management\Proof_of_Concept_QC\Full_Results\Loads\total_runoff.csv"
total_runoff_df = pd.read_csv(total_runoff_file, parse_dates=['Date'])
total_runoff_df = total_runoff_df.set_index('Date')

for root, dirs, files in os.walk(input_folder):
    for file in files:
        if 'SSM_Results' in file:
            path = os.path.join(root, file)
            watershed_df = pd.read_csv(path, parse_dates=['Date'])
            watershed_df = watershed_df.set_index('Date')

            for col in columns_to_convert:
                load_name = col.replace('mg/L', 'kg/d')
                watershed_df[load_name] = watershed_df['Runoff(m3/s)'] * watershed_df[col] * 86.4
                
            watershed_df['Total Flow Weighted Temperature (degC)'] = watershed_df[temperature_col] * watershed_df['Runoff(m3/s)'] / total_runoff_df['Runoff(m3/s)']

            watershed_df = watershed_df.drop(columns=columns_to_convert)
            out_file = file.replace("SSM_Results", "SSM_Loads")
            watershed_df.to_csv(os.path.join(output_folder, out_file))

            runoff = watershed_df['Runoff(m3/s)']


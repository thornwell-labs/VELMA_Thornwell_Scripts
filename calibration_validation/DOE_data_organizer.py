"""
Splits the Washington Ecology EIM discrete results dataset into one CSV per
parameter of interest (flow, temperature, ammonia, nitrate+nitrite, TOC, DOC),
making the large dataset easier to work with downstream.
"""

import pandas as pd


parameters = ['Flow', 'Temperature, water', 'Ammonia', 'Nitrate + Nitrite as N',
              'Total Organic Carbon', 'Dissolved Organic Carbon']
file_path = 'path/to/VELMA_Tools/DOE_Data/EIMDiscreteResults_2023Oct31_171413.csv'
out_root = 'path/to/VELMA_Tools/DOE_Data/'
full_doe_df = pd.read_csv(file_path)

# Extract columns of interest from doe_df


filtered_df = full_doe_df[full_doe_df['Result_Parameter_Name'].isin(parameters)]
for parameter in parameters:
    out_path = f'{out_root}{parameter}_DiscreteResults.csv'
    parameter = [parameter]
    parameter_df = filtered_df[filtered_df['Result_Parameter_Name'].isin(parameter)]
    parameter_df.to_csv(out_path, index=False)
    
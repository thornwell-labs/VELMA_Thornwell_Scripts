"""
Extracts unique monitoring locations (with coordinates) for parameters of
interest from the Washington Ecology EIM discrete results dataset, writing a
deduplicated locations CSV for mapping available observation sites.
"""

import pandas as pd


parameters = ['Flow', 'Temperature, water', 'Ammonia', 'Nitrate + Nitrite as N',
              'Total Organic Carbon', 'Dissolved Organic Carbon']
columns = ['Location_ID', 'Result_Parameter_Name', 'Calculated_Latitude_Decimal_Degrees_NAD83HARN',
           'Calculated_Longitude_Decimal_Degrees_NAD83HARN']
file_path = 'path/to/obs_data/obs_data/EIMDiscreteResults_2023Oct31_171413.csv'
out_path = 'path/to/obs_data/obs_data/filtered_locations.csv'
doe_df = pd.read_csv(file_path)

# Extract columns of interest from doe_df
doe_df = doe_df[columns]

filtered_df = doe_df[doe_df['Result_Parameter_Name'].isin(parameters)]
filtered_df = filtered_df.drop_duplicates()

filtered_df.to_csv(out_path, index=False)

"""
Builds a detailed inventory of Washington Ecology monitoring locations.
For each location and parameter of interest, records the period of record,
data length, and whether co-located flow data exist (needed for unit
conversion), writing the result to locations_detailed.csv.
"""

import pandas as pd

locations_file = 'path/to/VELMA_Tools/DOE_Data/locations.csv'
doe_file = 'path/to/VELMA_Tools/DOE_Data/EIMDiscreteResults_2023Oct31_171413.csv'
out_file = 'path/to/VELMA_Tools/DOE_Data/locations_detailed.csv'
parameters_of_interest = ['Nitrate + Nitrite as N',
                          'Ammonia',
                          'Total Organic Carbon',
                          'Dissolved Organic Carbon',
                          'Temperature, water']

# Read in files to dataframes with desired columns
location_df = pd.read_csv(locations_file)
ecology_df = pd.read_csv(doe_file, usecols=['Location_ID', 'Field_Collection_Start_Date', 'Result_Parameter_Name'], parse_dates=['Field_Collection_Start_Date'])

# Obtain list of unique locations
locations_list = []
for location_id in location_df['Location ID']:
    if location_id in locations_list:
        continue
    else:
        locations_list.append(location_id)

# Create a copy of location_df with some additional columns: ['Start Date', 'End Date', 'Flow Flag', 'Cell Index']
output_df = location_df.copy()
output_df['Start Date'] = pd.NaT
output_df['End Date']   = pd.NaT
output_df['Flow Flag']  = None
output_df['Data Length'] = None

for location_id in locations_list:
    for parameter in parameters_of_interest[:-1]:  # exclude temperature because it doesn't require flow for a unit conversion
        loc_filtered = location_df[location_df['Location ID'] == location_id]
        if parameter in loc_filtered['Parameter'].values:
            flow_exists = loc_filtered['Parameter'].str.contains('Flow', case=False, na=False).any()
            output_df.loc[(output_df['Location ID'] == location_id) & (output_df['Parameter'] == parameter),
                          'Flow Flag'] = flow_exists

for location_id in locations_list:
    for parameter in parameters_of_interest:
        subset = ecology_df[(ecology_df['Location_ID'] == location_id) & (ecology_df['Result_Parameter_Name'] == parameter)]
        # Generate a list of all the values in the ['Field_Collection_Start_Date'] column
        # Extract the earliest and latest collection start dates
        if not subset.empty:
            output_df.loc[output_df['Location ID'] == location_id, 'Data Length'] = len(subset)
            min_date = subset['Field_Collection_Start_Date'].min()
            max_date = subset['Field_Collection_Start_Date'].max()
            output_df.loc[output_df['Location ID'] == location_id, 'Start Date'] = min_date
            output_df.loc[output_df['Location ID'] == location_id, 'End Date'] = max_date

# inspect or save out
output_df.to_csv(out_file, index=False)
print(f"Done: wrote to {out_file}")

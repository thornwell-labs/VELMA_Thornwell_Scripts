"""
Creates VELMA-format observed data files from Washington Department of Ecology
EIM monitoring data. Filters the Ecology dataset by location and parameter
(ammonia, nitrate+nitrite, DOC, temperature), converts mg/L concentrations to
VELMA units using simulated flow and watershed area, and writes one daily
observation file per parameter.
"""

import pandas as pd

ecology_data_file = 'path/to/VELMA_Tools/DOE_Data/EIMDiscreteResults_2023Oct31_171413.csv'

observed_folder_path = 'path/to/VELMA_Watersheds/Skagit/Data_Inputs30m/m_7_Observed'
flow_results_file = 'path/to/VELMA_Watersheds/Skagit/Results/MULTI_WA_Skagit30m_8Jul2025_resampled_3_Hyak/Results_1690562/DailyResults.csv'
watershed = 'Skagit'
location_id = '04A100'
area = 446100*90*90  # Important: this area MUST correspond to the contributing watershed area to this specific location ID!
model_start_year = 1987
model_end_year = 2021

# Specify parameters that can be collected from the Ecology data
parameters = ['Ammonia', 'Nitrate + Nitrite as N', 'Dissolved Organic Carbon', 'Temperature, water']

# Load relevant columns from Ecology data and results file
ecology_df = pd.read_csv(ecology_data_file, usecols=['Location_ID', 'Field_Collection_Start_Date', 'Result_Parameter_Name', 'Result_Value', 'Result_Value_Units'])
sim_df = pd.read_csv(flow_results_file, usecols=['Year', 'Day', 'Runoff_All(mm/day)_Delineated_Average'])
sim_df['Date'] = pd.to_datetime(sim_df['Year'].astype(str) + sim_df['Day'].astype(str), format='%Y%j')
sim_df.set_index('Date', inplace=True)

# Filter by location ID
ecology_df = ecology_df[ecology_df['Location_ID'] == location_id]

# Dates should be parsed as datetime objects
ecology_df['Field_Collection_Start_Date'] = pd.to_datetime(ecology_df['Field_Collection_Start_Date'])

for parameter in parameters:
    # Filter for the current parameter and flow
    filtered_ecology_df = ecology_df[ecology_df['Result_Parameter_Name'] == parameter]

    # Create date range covering the model period
    date_range = pd.date_range(start=f'{model_start_year}-01-01', end=f'{model_end_year}-12-31', freq='D')
    output_df = pd.DataFrame({'Date': date_range})

    # Set date as index in both dataframes
    output_df.set_index('Date', inplace=True)
    filtered_ecology_df.set_index('Field_Collection_Start_Date', inplace=True)

    # Create empty columns
    output_df['Value'] = None
            
    # Fill in Value where both concentration and flow data is available or set to 'NaN'
    for date in output_df.index:
        if date in filtered_ecology_df.index:
            row = filtered_ecology_df.loc[date]
            if parameter == 'Temperature, water':  # No unit conversion required if the parameter is temperature
                output_df.at[date, 'Value'] = row['Result_Value']
            else:  # For all other parameters, need to convert mg/L to g/m2
                flow_row = ecology_df[(ecology_df['Result_Parameter_Name'] == 'Flow') & (ecology_df['Field_Collection_Start_Date'] == date)]
                if not flow_row.empty:
                    flow = flow_row.iloc[0]['Result_Value']
                    concentration = row['Result_Value']
                    # g/m2 = [(C mg/L)*(1000 L/m3)*(Q mm/d)*(1 m/1000 mm)*(1 g/1000 mg)
                    value_g_m2 = concentration * 28.317 * flow * 86400 / 1000 / area
                    output_df.at[date, 'Value'] = value_g_m2
                else:
                    flow_row = sim_df.loc[date]
                    flow = flow_row['Runoff_All(mm/day)_Delineated_Average']
                    concentration = row['Result_Value']
                    # g/m2 = (C mg/L)*(1000 L/m3)*(Q mm/d)*(1 m/1000 mm)*(1 g/1000 mg)
                    # g/m2 = C * Q  / 1000
                    value_g_m2 = concentration * flow / 1000
                    output_df.at[date, 'Value'] = value_g_m2
                    print(f'{parameter} value at {date} did not have associated flow data. Used VELMA simulated data.')
        else:
            output_df.at[date, 'Value'] = 'NaN'

    # Reset index to turn Date back into a column
    output_df.reset_index(inplace=True)
    
    # Drop Date column
    output_df.drop(columns=['Date'], inplace=True)

    # Remove white spaces from parameter for filename
    safe_param = parameter.replace(' ', '_').replace('+', 'plus')

    # Save the resulting DataFrame without an index or headers
    out_name = f'{observed_folder_path}/Ecology_{location_id}_{watershed}_{safe_param}_{model_start_year}-{model_end_year}.csv'
    output_df.to_csv(out_name, index=False, header=False)
    print(f'{parameter} observed data file written to {out_name}')
    
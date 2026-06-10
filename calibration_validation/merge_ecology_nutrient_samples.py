"""
Merges Washington Ecology ammonia and nitrate-nitrite sample data into an
existing comparison table by date, producing a combined CSV of observed
nutrient concentrations for one monitoring location.
"""

import pandas as pd

root_directory = 'path/to/VELMA_Watersheds/Samish/'

ammonia_data = pd.read_csv(root_directory+'Samish Ecology Ammonia 03B050.csv')
nitrate_data = pd.read_csv(root_directory+'Samish Ecology Nitrate-Nitrite 03B050.csv')

combined_data = pd.read_csv(root_directory+'Ecology data comparison.csv', usecols=['Date', 'Observed Nitrate + Nitrite at 03B050 (mg/L)', 'Observed Ammonia at 03B050 (mg/L)'])

combined_data['Date'] = pd.to_datetime(combined_data['Date'])
ammonia_data['Date'] = pd.to_datetime(ammonia_data['Field_Collection_Start_Date'])
nitrate_data['Date'] = pd.to_datetime(nitrate_data['Field_Collection_Start_Date'])

# Merge ammonia data into combined_data
combined_data = combined_data.merge(
    ammonia_data[['Date', 'Result_Value']],
    on='Date',
    how='left'
)
combined_data['Ecology Ammonia Concentration (mg/L)'] = combined_data['Result_Value']
combined_data = combined_data.drop(columns=['Result_Value'])

# Merge nitrate data into combined_data
combined_data = combined_data.merge(
    nitrate_data[['Date', 'Result_Value']],
    on='Date',
    how='left'
)
combined_data['Ecology Nitrate Concentration (mg/L)'] = combined_data['Result_Value']
combined_data = combined_data.drop(columns=['Result_Value'])

# Save or view the updated combined_data
print(combined_data.head())
combined_data.to_csv(root_directory+'Ammonia_Nitrate.csv')

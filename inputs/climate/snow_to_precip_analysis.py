"""
Compiles snow and rain time series from decadal PSIMF VELMA result folders and
computes the snow-to-total-precipitation ratio. Writes by-date and by-year
CSVs summarizing how the snow fraction changes across the simulated decades.
"""

import pandas as pd
import os

watershed = 'Issaquah'
base = 'path/to/VELMA_Watersheds/Issaquah/Results'
# outlet = '244276'
# base = 'path/to/hpc/Stillaguamish/Results/'
result_folders = [
    'MULTI_WA_Issaquah30m_PSIMF_16July2025_Hyak',
    'MULTI_WA_Issaquah30m_PSIMF_2029_Hyak',
    'MULTI_WA_Issaquah30m_PSIMF_2039_Hyak',
    'MULTI_WA_Issaquah30m_PSIMF_2049_Hyak',
    'MULTI_WA_Issaquah30m_PSIMF_2059_Hyak',
    'MULTI_WA_Issaquah30m_PSIMF_2069_Hyak',
    'MULTI_WA_Issaquah30m_PSIMF_2079_Hyak',
    'MULTI_WA_Issaquah30m_PSIMF_2089_Hyak',
    'MULTI_WA_Issaquah30m_PSIMF_2099_Hyak'
]

df_by_decade = {}

for folder in result_folders:
    for root, dirs, files in os.walk(os.path.join(base, folder)):
        for file in files:
            if 'DailyResults.csv' in file:
                file_path = os.path.join(root, file)
                df = pd.read_csv(file_path, usecols=['Year', 'Day', 'Snow(mm/day)_Delineated_Average', 'Rain(mm/day)_Delineated_Average'])
                df['Date'] = pd.to_datetime(df['Year'].astype(str), format='%Y') + pd.to_timedelta(df['Day'] - 1, unit='D')
                df = df[df['Year'] >= 2010]
                df['Snow(mm_day)'] = df['Snow(mm/day)_Delineated_Average']
                df['Rain(mm_day)'] = df['Rain(mm/day)_Delineated_Average']
                df = df[['Date', 'Snow(mm_day)', 'Rain(mm_day)']]
    df_by_decade[folder] = df
    
all_data = pd.concat(df_by_decade.values(), keys=df_by_decade.keys(), names=['Decade'])
all_data = all_data.reset_index(level='Decade', drop=True)
all_data = all_data.set_index('Date')
all_data['Total_Precipitation(mm_day)'] = all_data['Snow(mm_day)'] + all_data['Rain(mm_day)'] 
all_data['Snow_to_Total_P'] = all_data['Snow(mm_day)'] / all_data['Total_Precipitation(mm_day)']
all_data.to_csv(os.path.join(base, f'{watershed}_PSIMF_Snow_Rain_By_Date.csv'))

all_data['Year'] = all_data.index.year
annual = all_data.groupby('Year')[['Snow(mm_day)', 'Rain(mm_day)', 'Total_Precipitation(mm_day)']].sum()
annual['Mean_Snow_to_Total_P'] = all_data.groupby('Year')['Snow_to_Total_P'].mean()
annual.to_csv(os.path.join(base, f'{watershed}_PSIMF_Snow_Rain_By_Year.csv'))

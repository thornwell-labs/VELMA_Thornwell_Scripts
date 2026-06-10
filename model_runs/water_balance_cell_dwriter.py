"""
Visualizes the water balance at a single VELMA cell over specified year(s)
using a cell data writer CSV. Sums precipitation, evapotranspiration, lateral
inflow/outflow, and runoff component columns and plots them together.
"""

import pandas as pd
import matplotlib.pyplot as plt

# User must specify these values
data_file = ('path/to/VELMA_Watersheds/Hoko/Hoko_Working/Results/'
             'MULTI_WA_Hoko30m_ParMulti_800mPRISM_18cover_7June24/Results_100002/Cell_i100002_x299_y179_dlnWriter.csv')
data_columns_ET = ['ET_Actual(mm/day)_Layer1', 'ET_Actual(mm/day)_Layer2',
                   'ET_Actual(mm/day)_Layer3', 'ET_Actual(mm/day)_Layer4']
data_columns_Precip = ['Snow(mm/day)', 'Rain(mm/day)']
data_columns_Inflow = ['Water_Inflow(mm/day)', 'Lateral_Inflow(mm/day)_Layer1', 'Lateral_Inflow(mm/day)_Layer2',
                       'Lateral_Inflow(mm/day)_Layer3', 'Lateral_Inflow(mm/day)_Layer4']
data_columns_Outflow = ['Lateral_Outflow(mm/day)_Layer1',
                        'Lateral_Outflow(mm/day)_Layer2', 'Lateral_Outflow(mm/day)_Layer3',
                        'Lateral_Outflow(mm/day)_Layer4']
data_columns_runoff = ['Surface_Lateral_Outflow(mm/day)']
y_label = 'Water Transport (mm/day)'
title = 'Water Balance in 2015'
years = [2015]
# The names below will control the legend items
sum_name_Precip = 'Precipitation (Rain+Snow)'
sum_name_ET = 'Evapotranspiration'
sum_name_inflow = 'Lateral Inflow'
sum_name_outflow = 'Lateral Outflow'
sum_name_runoff = 'Runoff'

# Read in the file and filter it by the year(s) of interest
df = pd.read_csv(data_file)
df_filtered = df[df['Year'].isin(years)].copy()
df_filtered['Date'] = pd.to_datetime(df_filtered['Year'].astype(str) + df_filtered['Jday'].astype(str), format='%Y%j')

# Sum columns as needed and rename them
df_filtered[sum_name_Precip] = df_filtered[data_columns_Precip].sum(axis=1)
data_columns_Precip = [sum_name_Precip]

df_filtered[sum_name_ET] = df_filtered[data_columns_ET].sum(axis=1)
data_columns_ET = [sum_name_ET]

df_filtered[sum_name_inflow] = df_filtered[data_columns_Inflow].sum(axis=1)
data_columns_Inflow = [sum_name_inflow]

df_filtered[sum_name_outflow] = df_filtered[data_columns_Outflow].sum(axis=1)
data_columns_Outflow = [sum_name_outflow]

df_filtered[sum_name_runoff] = df_filtered[data_columns_runoff]
data_columns_runoff = [sum_name_runoff]

# Plot the data

# For line chart:
# plt.figure(figsize=(10, 6))
# data_columns = data_columns_Precip+data_columns_ET+data_columns_Outflow+data_columns_Inflow
# for column in data_columns:
#     plt.plot(df_filtered['Jday'], df_filtered[column], label=column)

# For stacked filled line chart:
data_columns = (data_columns_Precip+data_columns_ET+data_columns_Outflow+data_columns_Inflow)
y_list = []
for column in data_columns:
    y_list.append(df_filtered[column])
plt.stackplot(df_filtered['Date'], y_list, labels=data_columns)

# For stacked bar chart:
# plt.figure(figsize=(10, 6))
# data_columns = (data_columns_Precip+data_columns_ET+data_columns_Outflow+data_columns_Inflow)
# bar_height = [0] * len(df_filtered)
# for column in data_columns:
#     plt.bar(df_filtered['Date'], df_filtered[column], bottom=bar_height, label=column)
#     bar_height = [i+j for i, j in zip(bar_height, df_filtered[column])]

plt.xlabel('Date')
plt.ylabel(y_label)
plt.title(title)
plt.legend()
plt.grid(True)
plt.show()

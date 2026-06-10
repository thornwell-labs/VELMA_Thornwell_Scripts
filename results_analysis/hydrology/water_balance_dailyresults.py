"""
Visualizes the watershed-scale water balance from a VELMA DailyResults file
over specified year(s). Sums precipitation, evapotranspiration, storage, and
runoff columns and plots them together. Watershed-level counterpart to
water_balance_cell_dwriter.py.
"""

import pandas as pd
import matplotlib.pyplot as plt

# User must specify these values
data_file = ('path/to/VELMA_Watersheds/Dungeness/Dungeness_Working/Results/'
             'MULTI_WA_Dungeness_30m_27Sep2024/Results_72088/DailyResults.csv')
data_columns_ET = ['ET(mm/day)_Delineated_Average']
data_columns_Storage = ['Standing_Water(mm)_Delineated_Average',
                        'Water_Stored(mm)_Delineated_Average_Layer_1', 'Water_Stored(mm)_Delineated_Average_Layer_2',
                        'Water_Stored(mm)_Delineated_Average_Layer_3', 'Water_Stored(mm)_Delineated_Average_Layer_4']
data_columns_Precip = ['Snow(mm/day)_Delineated_Average', 'Rain(mm/day)_Delineated_Average']
data_columns_runoff = ['Runoff_All(mm/day)_Delineated_Average']
y_label = 'Water Balance (mm)'
title = 'Water Balance in 1991'
years = [1991]
# The names below will control the legend items
sum_name_Precip = 'Precipitation (Rain+Snow)'
sum_name_ET = 'Evapotranspiration'
sum_name_runoff = 'Runoff'
sum_name_storage = 'Storage'

# Read in the file and filter it by the year(s) of interest
df = pd.read_csv(data_file)
df_filtered = df[df['Year'].isin(years)].copy()
df_filtered['Date'] = pd.to_datetime(df_filtered['Year'].astype(str) + df_filtered['Day'].astype(str), format='%Y%j')

# Sum columns as needed and rename them
df_filtered[sum_name_Precip] = df_filtered[data_columns_Precip].sum(axis=1)
data_columns_Precip = [sum_name_Precip]

df_filtered[sum_name_ET] = df_filtered[data_columns_ET].sum(axis=1)
data_columns_ET = [sum_name_ET]

df_filtered[sum_name_storage] = df_filtered[data_columns_Storage].sum(axis=1)
data_columns_Storage = [sum_name_storage]

df_filtered[sum_name_runoff] = df_filtered[data_columns_runoff]
data_columns_runoff = [sum_name_runoff]

# Plot the data

# For line chart:
# plt.figure(figsize=(10, 6))
# data_columns = data_columns_Precip+data_columns_ET+data_columns_Outflow+data_columns_Inflow
# for column in data_columns:
#     plt.plot(df_filtered['Jday'], df_filtered[column], label=column)

# For stacked filled line chart:
data_columns = (data_columns_Precip+data_columns_ET+data_columns_runoff)
# data_columns_Storage
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

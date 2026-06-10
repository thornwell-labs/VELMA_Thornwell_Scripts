"""
Plots a chosen VELMA variable (e.g. NH4, runoff, temperature) over time for
selected year(s) from one or more daily results or cell data writer files,
overlaying multiple scenarios on a single line plot. Optionally sums
multi-layer variables. Base version of the daily_visualizer family.
"""

# Takes daily data at a specified cell data writer or average delineated results file for a specified data type(s),
# and displays the value over time for a specified year(s) in a line plot.
# Only generates one plot at a time.

import pandas as pd
import matplotlib.pyplot as plt

# User must specify these values
# Data files must be the same type (either daily results or cell data writers)
data_files = {'Public Septic Data': r"path\to\VELMA_Watersheds\Big_Beef\Results\WA_BigBeef30m_Historical_SepticTest\Results_23023\DailyResults.csv",
              'MOU Septic Data': r"path\to\VELMA_Watersheds\Big_Beef\Results\MULTI_WA_BigBeef30m_5Dec2025\Results_23023\DailyResults.csv",
              }
years = range(1990, 2022)
sum_columns = True  # Set to True to see one value, or False to see individual layers
data_to_plot = 'NH4'
# List of possible values for data_to_plot:
# Evapotranspiration, Snow dynamics, Nitrate, NH4, DON, DOC, Temperature, Biomass, Detritus, Humus, Runoff

# Code will run without editing anything below this line

# This block determines whether the file is from a cell data writer or has average delineated results
if 'DailyResults' in data_files.values():
    file_switch = True
else:
    file_switch = False

# This block takes care of title formatting
years_string = ''
for year in years:
    if len(years_string) == 0:
        years_string = f'{year}'
    else:
        years_string = years_string+f', {year}'
    if len(years) >= 5:
        years_string = f'{years[0]} to {years[-1]}'


# This class and the following dictionary contain all the information needed to plot the data of interest
# May need to add more information to parameter_groups dictionary in the future
class ParameterGroups:
    def __init__(self, y_label=None, title=None, data_columns=None, data_columns2=None, sum_name=None):
        self.data_columns = data_columns if file_switch else data_columns2
        # data_columns are used for cell data writer results; data_columns2 are used for average delineated results
        self.y_label = y_label
        self.title = title
        self.sum_name = sum_name


parameter_groups = {
    'Runoff': ParameterGroups(data_columns=['Runoff_All(mm/day)_Delineated_Average'],
                                          data_columns2=['Runoff_All(mm/day)_Delineated_Average'],
                                          y_label='Runoff (mm/day)',
                                          title=f'Runoff in {years_string}',
                                          sum_name='Runoff(mm/day)'),
    
    
    'Evapotranspiration': ParameterGroups(data_columns=['ET_Actual(mm/day)_Layer1', 'ET_Actual(mm/day)_Layer2',
                                                        'ET_Actual(mm/day)_Layer3', 'ET_Actual(mm/day)_Layer4'],
                                          data_columns2=['ET(mm/day)_Delineated_Average'],
                                          y_label='Evapotranspiration (mm/day)',
                                          title=f'Evapotranspiration in {years_string}',
                                          sum_name='Total ET_Actual(mm/day)'),

    'Snow dynamics': ParameterGroups(data_columns2=['Snow(mm/day)_Delineated_Average',
                                                    'Snow_Depth(mm)_Delineated_Average',
                                                    'Snow_Melt(mm/day)_Delineated_Average'],
                                     data_columns=['Snow(mm/day)', 'Snow_Depth(mm)', 'Snow_Melt(mm/day)'],
                                     y_label='Snow (mm)',
                                     title=f'Snow Dynamics in {years_string}'),

    'Nitrate': ParameterGroups(data_columns2=['NO3_Pool(gN/m2)_Delineated_Average'],
                               data_columns=['Surface_NO3(gN/day/m2)', 'NO3(gN/m2)_Layer1', 'NO3(gN/m2)_Layer2',
                                             'NO3(gN/m2)_Layer3', 'NO3(gN/m2)_Layer4'],
                               y_label='Nitrate (gN/m2)',
                               title=f'Nitrate in {years_string}',
                               sum_name='Nitrate (gN/m2)'),

    'NH4': ParameterGroups(data_columns2=['NH4_Pool(gN/m2)_Delineated_Average'],
                           data_columns=['Surface_NH4(gN/day/m2)', 'NH4(gN/m2)_Layer1', 'NH4(gN/m2)_Layer2',
                                         'NH4(gN/m2)_Layer3', 'NH4(gN/m2)_Layer4'],
                           y_label='NH4 (gN/m2)',
                           title=f'NH4 in {years_string}',
                           sum_name='NH4 (gN/m2)'),

    'DON': ParameterGroups(data_columns2=['DON_Pool(gN/m2)_Delineated_Average'],
                           data_columns=['Surface_DON(gN/day/m2)', 'DON(gN/m2)_Layer1', 'DON(gN/m2)_Layer2',
                                         'DON(gN/m2)_Layer3', 'DON(gN/m2)_Layer4'],
                           y_label='DON (gN/m2)',
                           title=f'DON in {years_string}',
                           sum_name='DON (gN/m2)'),

    'DOC': ParameterGroups(data_columns2=['DOC_Pool(gC/m2)_Delineated_Average'],
                           data_columns=['Surface_DOC(gC/day/m2)', 'DOC(gC/m2)_Layer1', 'DOC(gC/m2)_Layer2',
                                         'DOC(gC/m2)_Layer3', 'DOC(gC/m2)_Layer4'],
                           y_label='DOC (gC/m2)',
                           title=f'DOC in {years_string}',
                           sum_name='DOC (gC/m2)'),

    'Temperature': ParameterGroups(data_columns=['Water_Surface_Temperature(degrees_C)',
                                                 'Water_Temperature(degrees_C)_Layer1',
                                                 'Water_Temperature(degrees_C)_Layer2',
                                                 'Water_Temperature(degrees_C)_Layer3',
                                                 'Water_Temperature(degrees_C)_Layer4'],
                                   data_columns2=['Ground_Surface_Temperature(degC)_Delineated_Average'],
                                   y_label='Water Temperature (degrees Celsius)',
                                   title=f'Water Temperature in {years_string}',
                                   sum_name='Water Temperature (degrees C)'),

    'Biomass': ParameterGroups(data_columns2=['Biomass_Pool(gC/m2)_Delineated_Average',
                                             'agBiomass_Pool(gC/m2)_Delineated_Average',
                                             'bgBiomass_Pool(gC/m2)_Delineated_Average',
                                              'Biomass_Leaf(gC/m2)_Delineated_Average'],
                               data_columns=['Biomass(gN/m2)', 'Biomass_Leaf_N(gN/m2)', 'Biomass_AgStem_N(gN/m2)',
                                             'Biomass_BgStem_N(gN/m2)', 'Biomass_Root_N(gN/m2)_Layers_SUM'],
                               y_label='Biomass (gC/m2)',
                               title=f'Biomass in {years_string}',
                               sum_name='Biomass (gC/m2)'),

    'Detritus': ParameterGroups(data_columns2=['agLitter_Pool(gC/m2)_Delineated_Average',
                                               'bgLitter_Pool(gC/m2)_Delineated_Average'],
                                data_columns=['Detritus_Leaf_N(gN/m2)', 'Detritus_Root_N(gN/m2)_Layers_SUM',
                                              'Detritus_BgStem_N(gN/m2)_Layer1', 'Detritus_BgStem_N(gN/m2)_Layer2',
                                              'Detritus_BgStem_N(gN/m2)_Layer3', 'Detritus_BgStem_N(gN/m2)_Layer4'],
                                y_label='Detritus (gC/m2)',
                                title=f'Detritus in {years_string}',
                                sum_name='Detritus (gC/m2)'),

    'Humus': ParameterGroups(data_columns2=['Humus_Pool(gC/m2)_Delineated_Average',
                                            'Humus(gC/m2)_Delineated_Average_Layer_1',
                                            'Humus(gC/m2)_Delineated_Average_Layer_2',
                                            'Humus(gC/m2)_Delineated_Average_Layer_3',
                                            'Humus(gC/m2)_Delineated_Average_Layer_4'],
                             data_columns=['Humus(gN/m2)_Layer1', 'Humus(gN/m2)_Layer2',
                                           'Humus(gN/m2)_Layer3', 'Humus(gN/m2)_Layer4'],
                             y_label='Humus (gN/m2)',
                             title=f'Humus in {years_string}',
                             sum_name='Humus (gN/m2)')
                }


def plot_daily_data(params, data_file, years, sum_columns, file_switch):
    plt.figure(figsize=(10, 6))
    # Read in the data, filter by year(s) of interest and sum columns if needed
    for name, data_file in data_files.items():
        df = pd.read_csv(data_file)
        df_filtered = df[df['Year'].isin(years)].copy()
        if file_switch:
            df_filtered['Date'] = pd.to_datetime(df_filtered['Year'].astype(str) +
                                                df_filtered['Jday'].astype(str), format='%Y%j')
        else:
            df_filtered['Date'] = pd.to_datetime(df_filtered['Year'].astype(str) +
                                                df_filtered['Day'].astype(str), format='%Y%j')
        if sum_columns:
            df_filtered[params.sum_name] = df_filtered[params.data_columns].sum(axis=1)
            plot_columns = [params.sum_name]
        else:
            plot_columns = params.data_columns
        for column in plot_columns:
            plt.plot(df_filtered['Date'], df_filtered[column], label=name + ': ' + column)
        plt.xlabel('Date')
        plt.ylabel(params.y_label)
        plt.title(params.title)
        plt.legend()
        plt.grid(True)
    plt.show()


plot_daily_data(parameter_groups[data_to_plot], data_files, years, sum_columns, file_switch)

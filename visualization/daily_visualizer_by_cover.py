"""
Plots a chosen VELMA variable over time for selected year(s), with one line
per land cover type, using the per-cover average columns of a daily results
file. Cover-stratified variant of daily_visualizer.py.
"""

# Takes daily data at a specified cell data writer or average Cover results file for a specified data type(s),
# and displays the value over time for a specified year(s) in a line plot.
# Only generates one plot at a time.

import pandas as pd
import matplotlib.pyplot as plt

# User must specify these values
# Data file must be the daily results
data_file = r"path\to\VELMA_Watersheds\Stillaguamish\Results\MULTI_WA_Stillaguamish30m_30Jun2025_Hyak\Results_2100476\DailyResults.csv"
cover_types = ['Alder88Percent_9', 'MixedForest_43', 'EvergreenForest_42', 'ShrubScrub_52']

#              ['Alder37Percent_7', 'Alder17Percent_6', 'Alder5Percent_5','Alder88Percent_9', 'Alder62Percent_8', 'MixedForest_43', 'EvergreenForest_42', 'Wetlands_90', 'ShrubScrub_52']
#              ['DevelopedMediumIntensity_23', 'DevelopedOpenSpace_21', 'DevelopedLowIntensity_22', 'DevelopedHighIntensity_24', 'BareLand_31']
#              ['SnowIce_12', 'Water_11']
#              ['Grassland_71', 'Pasture_81', 'Cultivated_82']
# Must match cover type names exactly
years = range(1990, 2022)
sum_columns = True  # Set to True to see one value, or False to see individual layers
data_to_plot = 'Detritus'
# List of possible values for data_to_plot:
# Evapotranspiration, NPP, Snow dynamics, Nitrate, NH4, DON, DOC, Temperature, Biomass, Detritus

# Code will run without editing anything below this line

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
    def __init__(self, y_label=None, title=None, data_columns=None, sum_name=None):
        self.data_columns = data_columns
        self.y_label = y_label
        self.title = title
        self.sum_name = sum_name


parameter_groups = {
    'Evapotranspiration': ParameterGroups(data_columns=['ET(mm/day)_Cover_Average'],
                                          y_label='Evapotranspiration (mm/day)',
                                          title=f'Evapotranspiration in {years_string}',
                                          sum_name='Total ET_Actual(mm/day)'),

    'NPP': ParameterGroups(data_columns=['NPP_C(gC/day/m2)_Cover_Average'],
                           y_label='NPP (gC/day/m2)',
                           title=f'NPP in {years_string}',
                           sum_name='NPP(gC/day/m2)'),

    'Snow dynamics': ParameterGroups(data_columns=['Snow(mm/day)_Cover_Average',
                                                    'Snow_Depth(mm)_Cover_Average',
                                                    'Snow_Melt(mm/day)_Cover_Average'],
                                     y_label='Snow (mm)',
                                     title=f'Snow Dynamics in {years_string}'),

    'Nitrate': ParameterGroups(data_columns=['NO3_Pool(gN/m2)_Cover_Average'],
                               y_label='Nitrate (gN/m2)',
                               title=f'Nitrate in {years_string}',
                               sum_name='Nitrate (gN/m2)'),

    'NH4': ParameterGroups(data_columns=['NH4_Pool(gN/m2)_Cover_Average'],
                           y_label='NH4 (gN/m2)',
                           title=f'NH4 in {years_string}',
                           sum_name='NH4 (gC/m2)'),

    'DON': ParameterGroups(data_columns=['DON_Pool(gN/m2)_Cover_Average'],
                           y_label='DON (gN/m2)',
                           title=f'DON in {years_string}',
                           sum_name='DON (gN/m2)'),

    'DOC': ParameterGroups(data_columns=['DOC_Pool(gC/m2)_Cover_Average'],
                           y_label='DOC (gC/m2)',
                           title=f'DOC in {years_string}',
                           sum_name='DOC (gC/m2)'),

    'Temperature': ParameterGroups(data_columns=['Ground_Surface_Temperature(degC)_Cover_Average'],
                                   y_label='Water Temperature (degrees Celsius)',
                                   title=f'Water Temperature in {years_string}',
                                   sum_name='Water Temperature (degrees C)'),

    'Biomass': ParameterGroups(data_columns=['agBiomass_Pool(gC/m2)_Cover_Average',
                                             'bgBiomass_Pool(gC/m2)_Cover_Average'],
                               y_label='Biomass (gC/m2)',
                               title=f'Biomass in {years_string}',
                               sum_name='Biomass (gC/m2)'),

    'Detritus': ParameterGroups(data_columns=['agLitter_Pool(gC/m2)_Cover_Average',
                                               'bgLitter_Pool(gC/m2)_Cover_Average'],
                                y_label='Detritus (gC/m2)',
                                title=f'Detritus in {years_string}',
                                sum_name='Detritus (gC/m2)'),

    # 'Humus': ParameterGroups(data_columns=['Humus_Pool(gC/m2)_Cover_Average',
    #                                         'Humus(gC/m2)_Cover_Average_Layer_1',
    #                                         'Humus(gC/m2)_Cover_Average_Layer_2',
    #                                         'Humus(gC/m2)_Cover_Average_Layer_3',
    #                                         'Humus(gC/m2)_Cover_Average_Layer_4'],
    #                          y_label='Humus (gN/m2)',
    #                          title=f'Humus in {years_string}',
    #                          sum_name='Humus (gN/m2)')
                }


def plot_daily_data(params, data_file, years, sum_columns):
    plt.figure(figsize=(10, 6))
    # Read in the data, filter by year(s) of interest and sum columns if needed
    df = pd.read_csv(data_file)
    df_filtered = df[df['Year'].isin(years)].copy()
    df_filtered['Date'] = pd.to_datetime(df_filtered['Year'].astype(str) +
                                            df_filtered['Day'].astype(str), format='%Y%j')
    for cover in cover_types:
        column_names = [cover + '_' + column for column in params.data_columns]
        if sum_columns:
            df_filtered[cover + '_' + params.sum_name] = df_filtered[column_names].sum(axis=1)
            plot_columns = [cover + '_' + params.sum_name]
        else:
            plot_columns = [column_names]
        for column in plot_columns:
            plt.plot(df_filtered['Date'], df_filtered[column], label=column)
        plt.xlabel('Date')
        plt.ylabel(params.y_label)
        plt.title(params.title)
        plt.legend()
        plt.grid(True)
    plt.show()


plot_daily_data(parameter_groups[data_to_plot], data_file, years, sum_columns)

"""
Plots a chosen VELMA variable (e.g. humus) over time for selected year(s),
with one line per soil type, using the per-soil average columns of a daily
results file. Soil-stratified variant of daily_visualizer.py.
"""

# Takes daily data at a specified cell data writer or average Cover results file for a specified data type(s),
# and displays the value over time for a specified year(s) in a line plot.
# Only generates one plot at a time.

import pandas as pd
import matplotlib.pyplot as plt

# User must specify these values
# Data file must be the daily results
data_file = r"path\to\VELMA_Watersheds\Stillaguamish\Results\MULTI_WA_Stillaguamish30m_30Jun2025_Hyak\Results_2100476\DailyResults.csv"
soil_types = ['Medium_CN24', 'Medium_CN12', 'Medium_CN17']
# ['Medium_CN24', 'Medium_CN12', 'Medium_CN17']
# Must match soil type names exactly
years = range(1990, 2022)
data_to_plot = 'Humus'
# List of possible values for data_to_plot:
# Humus

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
    'Humus': ParameterGroups(data_columns=['Humus_Pool(gC/m2)_Soil_Average'],
                             y_label='Humus (gC/m2)',
                             title=f'Humus in {years_string}',
                             sum_name='Humus (gC/m2)')
                }


def plot_daily_data(params, data_file, years):
    plt.figure(figsize=(10, 6))
    # Read in the data, filter by year(s) of interest and sum columns if needed
    df = pd.read_csv(data_file)
    df_filtered = df[df['Year'].isin(years)].copy()
    df_filtered['Date'] = pd.to_datetime(df_filtered['Year'].astype(str) +
                                            df_filtered['Day'].astype(str), format='%Y%j')
    for soil in soil_types:
        column_names = [soil + '_' + column for column in params.data_columns]
        plot_columns = [column_names]
        for column in plot_columns:
            plt.plot(df_filtered['Date'], df_filtered[column], label=column)
        plt.xlabel('Date')
        plt.ylabel(params.y_label)
        plt.title(params.title)
        plt.legend()
        plt.grid(True)
    plt.show()


plot_daily_data(parameter_groups[data_to_plot], data_file, years)

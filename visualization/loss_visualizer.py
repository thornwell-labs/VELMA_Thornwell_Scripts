"""
Plots a chosen nitrogen or carbon loss variable over time for selected
year(s), comparing VELMA nitrogen-source-elimination scenarios on one line
plot, with optional overlay of observed Ecology data. Loss-focused variant of
daily_visualizer.py.
"""

# Takes daily data at a specified cell data writer or average delineated results file for a specified data type(s),
# and displays the value over time for a specified year(s) in a line plot.
# Only generates one plot at a time.

import pandas as pd
import matplotlib.pyplot as plt

# User must specify these values (must be daily results)
data_files = {'No Alder Nitrogen Fixation': 'path/to/VELMA_Watersheds/Samish/Results/MULTI_WA_Samish30m_Eliminate_Nitrogen_Fixation/Results_635473/DailyResults.csv',
              'No Fertilization': 'path/to/VELMA_Watersheds/Samish/Results/MULTI_WA_Samish30m_Eliminate_Fertilization/Results_635473/DailyResults.csv',
              'No Septic': 'path/to/VELMA_Watersheds/Samish/Results/MULTI_WA_Samish30m_Eliminate_Septic/Results_635473/DailyResults.csv',
              'No Deposition': 'path/to/VELMA_Watersheds/Samish/Results/MULTI_WA_Samish30m_Eliminate_Deposition/Results_635473/DailyResults.csv'
              }
years = range(2010, 2021)
sum_columns = True  # Set to True to see one value, or False to see individual layers
data_to_plot = 'Nitrate'
# List of possible values for data_to_plot:
# Nitrate, Ammonia, DON, TN, DOC

add_observed_data = False
observed_data_file = 'path/to/VELMA_Watersheds/Nooksack/Data_Inputs30m/m_7_Observed/Ecology_01A120_Nooksack_Ammonia_1987-2021.csv'
observed_start_year = 1987

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
    def __init__(self, y_label=None, title=None, data_columns=None):
        self.data_columns = data_columns
        self.y_label = y_label
        self.title = title


parameter_groups = {
    'TN': ParameterGroups(data_columns=['NO3_Loss(gN/day/m2)_Delineated_Average', 'NH4_Loss(gN/day/m2)_Delineated_Average',
                                        'DON_Loss(gN/day/m2)_Delineated_Average'],
                               y_label='Total Nitrogen Loss (gN/day/m2)',
                               title=f'Total Nitrogen Loss in {years_string}'),
    
    'Nitrate': ParameterGroups(data_columns=['NO3_Loss(gN/day/m2)_Delineated_Average'],
                               y_label='Nitrate Loss (gN/day/m2)',
                               title=f'Nitrate Loss in {years_string}'),

    'Ammonia': ParameterGroups(data_columns=['NH4_Loss(gN/day/m2)_Delineated_Average'],
                           y_label='Ammonia Loss (gN/day/m2)',
                           title=f'Ammonia Loss in {years_string}'),

    'DON': ParameterGroups(data_columns=['DON_Loss(gN/day/m2)_Delineated_Average'],
                           y_label='DON Loss (gN/day/m2)',
                           title=f'DON Loss in {years_string}'),

    'DOC': ParameterGroups(data_columns=['DOC_Loss(gC/day/m2)_Delineated_Average'],
                           y_label='DOC Loss (gC/day/m2)',
                           title=f'DOC Loss in {years_string}'),
                }


def plot_daily_data(params, data_file, years):
    plt.figure(figsize=(10, 6))
    # Read in the data, filter by year(s) of interest and sum columns if needed
    for name, data_file in data_files.items():
        df = pd.read_csv(data_file)
        df_filtered = df[df['Year'].isin(years)].copy()
        df_filtered['Date'] = pd.to_datetime(df_filtered['Year'].astype(str) +
                                            df_filtered['Day'].astype(str), format='%Y%j')
        plot_columns = params.data_columns
        df_filtered = df_filtered[['Year', 'Day', 'Date'] + plot_columns]
        if sum_columns == True:
            # Create a new column matching the y_label
            df_filtered[params.y_label] = df_filtered[plot_columns].sum(axis=1)
            plt.plot(df_filtered['Date'], df_filtered[params.y_label], label=name + ': ' + params.y_label)
        else:
            for column in plot_columns:
                plt.plot(df_filtered['Date'], df_filtered[column], label=name + ': ' + column)
        plt.xlabel('Date')
        plt.ylabel(params.y_label)
        plt.title(params.title)
        plt.grid(True)
        plt.legend()
    if add_observed_data:
        obs_df = pd.read_csv(observed_data_file, header=None, usecols=[0])
        obs_df.columns = [params.data_columns[0]]
        obs_df['Date'] = pd.date_range(start=f'{observed_start_year}-01-01', periods=len(obs_df), freq='D')
        obs_df.dropna(subset=[params.data_columns[0], 'Date'], inplace=True)
        obs_df['Year'] = obs_df['Date'].dt.year
        obs_df = obs_df[obs_df['Year'].isin(years)]
        plt.scatter(obs_df['Date'], obs_df[params.data_columns[0]], label=f'Observed {params.data_columns[0]}', color='black')
        plt.legend()        
    plt.show()


plot_daily_data(parameter_groups[data_to_plot], data_files, years)

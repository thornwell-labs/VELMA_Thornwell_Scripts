"""
Plots nitrogen-related variables (NH4/NO3 pools and losses, nitrification,
denitrification, NPP-N) by cover type, comparing two VELMA scenarios (e.g.
historical versus no alder nitrogen fixation) on shared axes.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

csv_files = {
    'Historical': r"path\to\DailyResults_Historical.csv",
    'No Alder Nitrogen Fixation': r"path\to\DailyResults_Eliminate_Nitrogen_Fixation.csv"
}

variable_list = ['ET(mm*m2/day/m2)_Cover_Average', 'NH4_Pool(gN/m2)_Cover_Average', 'NO3_Pool(gN/m2)_Cover_Average', 
               'NPP_N(gN/day/m2)_Cover_Average', 'NH4_Loss(gN/day/m2)_Cover_Average', 'NO3_Loss(gN/day/m2)_Cover_Average',
               'Nitrification(gN/day/m2)_Cover_Average_Layer_1', 'Denitrification(gN/day/m2)_Delineated_Average_Layer_1',
               'Disturbance_N_Added(gN/m2)_Cover_Average']

cover_list = ['Alder88Percent_9_', 'Alder37Percent_7_', 'EvergreenForest_42_']

cover_colors = {
    'Alder88Percent_9_': 'tab:green',
    'Alder37Percent_7_': 'tab:orange',
    'EvergreenForest_42_': 'tab:blue'
}

scenario_styles = {
    'Historical': '-',
    'No Alder Nitrogen Fixation': '--'
}

out_folder = r"path\to\VELMA_Watersheds\Samish\Analysis\Nitrogen_Sources"
        
# Build list of dates: 1/1/1989 through 12/31/2021
date_list = pd.date_range(start='1989-01-01', end='2021-12-31', freq='D')

for variable in variable_list:
    variable_name = variable.split('_')[0]
    columns_to_plot = []
    for cover in cover_list:
        col_name = cover + variable
        columns_to_plot.append(col_name)
        
    # Instantiate line plot using matplotlib
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title(variable)
    ax.set_xlabel('Date')
    ax.set_ylabel(variable)

    start_date = pd.Timestamp('2015-01-01')
    end_date = pd.Timestamp('2015-12-31')
    
    # Fill in the data
    for scenario_name, file_path in csv_files.items():
        df = pd.read_csv(file_path, usecols=columns_to_plot)
        for cover in cover_list:
            col_to_plot = cover + variable
            ax.plot(
                date_list,
                df[col_to_plot],
                color=cover_colors[cover],
                linestyle=scenario_styles[scenario_name],
                label=f"{cover.split('(')[0]} {scenario_name}"
            )
            
    # Finish the plot and save
    ax.set_xlim(start_date, end_date)
    ax.legend()
    fig.tight_layout()
    variable_name = variable.split('(')[0]
    fig.savefig(os.path.join(out_folder, f'{variable_name}_comparison.png'))
    plt.close(fig)

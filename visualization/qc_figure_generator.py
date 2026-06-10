"""
Generates a batch of quality-control figures from a VELMA daily results file,
plotting multiple chemistry variables (nitrate, NH4, biomass, detritus, DON,
DOC) grouped by cover category. Output PNGs are typically bundled into a report
by qc_report_generator.py.
"""

import pandas as pd
import matplotlib.pyplot as plt

data_file = 'path/to/VELMA_Watersheds/Skokomish/Results/MULTI_WA_Skokomish30m_3Apr2025_Hyak/Results_1365037/DailyResults.csv'
output_folder = 'path/to/VELMA_Watersheds/Skokomish/Analysis/3April'
years = range(1990, 2022)
sum_columns = True  # Set to True to see one value, or False to see individual layers
data_to_plot = ['Nitrate', 'NH4', 'Biomass', 'Detritus', 'DON', 'DOC']

# -------------------------------------------------------------------------------------------------------------------------------- #

years_string = ''
for year in years:
    if len(years_string) == 0:
        years_string = f'{year}'
    else:
        years_string = years_string+f', {year}'
    if len(years) >= 5:
        years_string = f'{years[0]} to {years[-1]}'

cover_types_dict = {
'Forested Cover Types': ['Alder37Percent_7', 'Alder17Percent_6', 'Alder5Percent_5','Alder88Percent_9', 'Alder62Percent_8', 'MixedForest_43', 'EvergreenForest_42', 'Wetlands_90', 'ShrubScrub_52'],
'Developed Cover Types': ['DevelopedMediumIntensity_23', 'DevelopedOpenSpace_21', 'DevelopedLowIntensity_22', 'DevelopedHighIntensity_24', 'BareLand_31'],
'Water Cover Types': ['SnowIce_12', 'Water_11'],
'Cultivated Cover Types': ['Grassland_71', 'Pasture_81', 'Cultivated_82'],
}

class ParameterGroups:
    def __init__(self, y_label=None, title=None, data_columns=None, sum_name=None):
        self.data_columns = data_columns
        self.y_label = y_label
        self.title = title
        self.sum_name = sum_name


parameter_groups = {
    'Nitrate': ParameterGroups(data_columns=['NO3_Pool(gN/m2)_Cover_Average'],
                               y_label='Nitrate (gN/m2)',
                               title=f'Nitrate {years_string}',
                               sum_name='Nitrate (gN/m2)'),

    'NH4': ParameterGroups(data_columns=['NH4_Pool(gN/m2)_Cover_Average'],
                           y_label='NH4 (gN/m2)',
                           title=f'NH4 {years_string}',
                           sum_name='NH4 (gC/m2)'),

    'DON': ParameterGroups(data_columns=['DON_Pool(gN/m2)_Cover_Average'],
                           y_label='DON (gN/m2)',
                           title=f'DON {years_string}',
                           sum_name='DON (gN/m2)'),

    'DOC': ParameterGroups(data_columns=['DOC_Pool(gC/m2)_Cover_Average'],
                           y_label='DOC (gC/m2)',
                           title=f'DOC {years_string}',
                           sum_name='DOC (gC/m2)'),

    'Biomass': ParameterGroups(data_columns=['agBiomass_Pool(gC/m2)_Cover_Average',
                                             'bgBiomass_Pool(gC/m2)_Cover_Average'],
                               y_label='Biomass (gC/m2)',
                               title=f'Biomass {years_string}',
                               sum_name='Biomass (gC/m2)'),

    'Detritus': ParameterGroups(data_columns=['agLitter_Pool(gC/m2)_Cover_Average',
                                               'bgLitter_Pool(gC/m2)_Cover_Average'],
                                y_label='Detritus (gC/m2)',
                                title=f'Detritus {years_string}',
                                sum_name='Detritus (gC/m2)')
    }

def plot_daily_data(params, data_file, years, sum_columns, cover_types, label):
    fig, ax = plt.subplots(figsize=(10, 6))
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
            plot_columns = column_names

        for column in plot_columns:
            ax.plot(df_filtered['Date'], df_filtered[column], label=column)
    ax.set_xlabel('Date')
    ax.set_ylabel(params.y_label)
    ax.set_title(f'{params.title} in {label}')
    ax.legend()
    ax.grid(True)
    return fig

for data in data_to_plot:
    for label, cover_list in cover_types_dict.items():
        fig = plot_daily_data(parameter_groups[data], data_file, years, sum_columns, cover_list, label)
        fig.savefig(f'{output_folder}/3_{label}_{data}.png')
        plt.close()
        
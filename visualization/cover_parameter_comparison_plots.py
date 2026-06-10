"""
Plots how a VELMA cover-type parameter changed between model versions across
watersheds. Reads old/new parameter values from each sheet of a parameter-
changes workbook, filters to cover-specific parameters, and produces
comparison plots. See parameter_comparison_plots.py for the non-cover version.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Load and reshape all tabs ---
file_path = 'path/to/VELMA_Watersheds/Analysis/Nutrient_model_parameter_changes.xlsx'
# param_name = 'nh4MaximumUptakeRate'
# watershed = '30June_Puyallup'
cover = 'EvergreenForest_42'
out_path = 'path/to/VELMA_Watersheds/Analysis/Parameter Comparison Plots'
save_plot = True
excel = pd.ExcelFile(file_path)

records = []

for sheet in excel.sheet_names:
    df = pd.read_excel(excel, sheet_name=sheet)
    
    for _, row in df.iterrows():
        param = row['Parameter']
        old = row['Old Value']
        new = row['New Value']
        
        if param.startswith('cover/'):
            match = param.split('/')
            if len(match) == 3:
                cover_type = match[1]
                param_name = match[2]
                records.append({
                    'Watershed': sheet,
                    'CoverType': cover_type,
                    'ParameterName': param_name,
                    'OldValue': old,
                    'NewValue': new,
                })

# Combine into one dataframe
long_df = pd.DataFrame(records)


# Use this block to compare a single parameter for many cover types in one watershed
# subset = long_df[(long_df['Watershed'] == watershed) & (long_df['ParameterName'] == param_name)]
# plt.figure(figsize=(8,5))
# sns.barplot(data=subset, x='CoverType', y='NewValue', color='skyblue')

# # Add dotted lines for the old value
# for i, y in enumerate(subset['OldValue']):
#     plt.hlines(y, xmin=i - 0.2, xmax=i + 0.2, colors='gray', linestyles='dotted', linewidth=3, label='Old Value' if i == 0 else "")

# plt.title(f"{param_name} across Cover Types ({watershed})")
# plt.ylabel("New Parameter Value")
# plt.legend()
# plt.xticks(rotation=80)
# plt.tight_layout()
# plt.show()
# if save_plot == True:
#     plt.savefig(f'{out_path}/{watershed}_{param_name}_comparison.png')
# plt.close()

for param_name in ['no3MaximumUptakeRate', 'nh4MaximumUptakeRate', 'detritusLeafNmaxDecay']:
    # Use this block to compare a parameter in one cover type across watersheds
    subset = long_df[(long_df['CoverType'] == cover) & (long_df['ParameterName'] == param_name)]
    plt.figure(figsize=(8,5))
    sns.barplot(data=subset, x='Watershed', y='NewValue', color='skyblue')
    # Add dotted lines for the old value
    for i, y in enumerate(subset['OldValue']):
        plt.hlines(y, xmin=i - 0.2, xmax=i + 0.2, colors='gray', linestyles='dotted', linewidth=3, label='Old Value' if i == 0 else "")
    plt.title(f"{param_name} for {cover} Across Watersheds")
    plt.ylabel("New Parameter Value")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    # plt.show()
    if save_plot == True:
        plt.savefig(f'{out_path}/{cover}_{param_name}_comparison.png')
    plt.close()

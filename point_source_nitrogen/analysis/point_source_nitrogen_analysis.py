"""
Combines per-decade SSM-format results into continuous series for runs with
and without point-source nitrogen, writing combined CSVs per watershed (with
optional comparison plots) to quantify the point-source contribution.
"""

import pandas as pd
import os
import matplotlib.pyplot as plt

folder_path = 'path/to/PSIMF Management/PointSourceN_Analysis'
out_dir = os.path.join(folder_path, "Figures")
os.makedirs(out_dir, exist_ok=True)  # create folder if missing

with_point_source = {}
no_point_source = {}

for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith('csv'):
            name = file.split('_')[0]
            df = pd.read_csv(os.path.join(root, file), parse_dates=['Date'], index_col='Date')
            df = df[df.index.year >= 2010]
            if 'PointSourceN' in file:
                if name not in with_point_source.keys():
                    with_point_source[name] = df
                else:
                    with_point_source[name] = pd.concat([with_point_source[name], df])
            else:
                if name not in no_point_source.keys():
                    no_point_source[name] = df
                else:
                    no_point_source[name] = pd.concat([no_point_source[name], df])
for name, df in with_point_source.items():
    df.to_csv(f'{folder_path}/Combined/total_{name}_with_point_source.csv')
for name, df in no_point_source.items():
    df.to_csv(f'{folder_path}/Combined/total_{name}_no_point_source.csv')

# for name, df in with_point_source.items():
#     for column_name in ['NH4_Loss(mg/L)', 'NO3_Loss(mg/L)', 'DON_Loss(mg/L)', 'DOC_Loss(mg/L)']:
#         plt.figure()
#         plt.plot(df[column_name], label='With Point Source N')
#         plt.plot(no_point_source[name][column_name], label='Without Point Source N')
#         plt.title(f'{column_name} in {name}')
#         plt.legend()
#         safe_column_name = column_name.replace("/", "_").replace("\\", "_")
#         plt.savefig(os.path.join(out_dir, f'{name}_{safe_column_name}.png'))
#         plt.close()
                
"""
Concatenates per-decade SSM-format result CSVs (2019 through 2099) into one
continuous full-period file per watershed, writing the combined outputs to a
Full_Results folder.
"""

import pandas as pd
import os

root = 'path/to/PSIMF Management/Proof_of_Concept_QC'
output_folder = os.path.join(root, 'Full_Results')
os.makedirs(output_folder, exist_ok=True)

result_folders = [
    os.path.join(root, '2019_Results'),
    os.path.join(root, '2029_Results'),
    os.path.join(root, '2039_Results'),
    os.path.join(root, '2049_Results'),
    os.path.join(root, '2059_Results'),
    os.path.join(root, '2069_Results'),
    os.path.join(root, '2079_Results'),
    os.path.join(root, '2089_Results'),
    os.path.join(root, '2099_Results')
]

df_dict = {}
for dirpath, dirs, files in os.walk(result_folders[0]):
    for file in files:
        name = file.split('_')[0]
        df = pd.read_csv(os.path.join(dirpath, file), parse_dates=['Date'])
        df.set_index('Date', inplace=True)
        df_dict[name] = df

for folder in result_folders[1:]:
    for dirpath, dirs, files in os.walk(folder):
        for file in files:
            name = file.split('_')[0]
            df = pd.read_csv(os.path.join(dirpath, file), parse_dates=['Date'])
            df.set_index('Date', inplace=True)
            df_dict[name] = pd.concat([df_dict[name], df])

for name, df in df_dict.items():
    df.to_csv(os.path.join(output_folder, f'{name}_Full_PSIMF_SSM_Results.csv'))        

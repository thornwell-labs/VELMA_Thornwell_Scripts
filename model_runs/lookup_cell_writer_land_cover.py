"""
Looks up the land cover code for each VELMA cell data writer location. Reads a
CSV of cell data writer indices per watershed, converts each linear cell index
to row/column in that watershed's land cover raster, and records the land
cover code found there.
"""

import pandas as pd
import rasterio
import numpy as np

root_folder =r'path\to\VELMA_Watersheds'
lc_file_dict = {
    'Big Beef': r'\Big_Beef\DataInputs30m\m_5_Coverage\BigBeef_LandCover19.asc',
    'Dungeness': r'\Dungeness\Dungeness_Working\Data_Inputs30m\m_5_Coverage\Dungeness30m_LandCover19.asc',
    'Elwha': r'\Elwha\Elwha_Working\Data_Inputs30m\m_5_Coverage\Elwha30m_LandCover19.asc',
    'Green': r'\Green\Data_Inputs30m\m_5_Coverage\Green30m_LandCover19.asc',
    'Hoko': r'\Hoko\Hoko_Working\Data_Inputs30m\m_5_Coverage\Hoko30m_LandCover19.asc',
    'Huge': r'\Huge\Data_Inputs30m\m_5_Coverage\Huge30m_LandCover19.asc',
    'Nisqually': r'\Nisqually\Data_Inputs30m\m_5_Coverage\Nisqually30m_LandCover19.asc',
    'Nooksack': r'\Nooksack\Data_Inputs30m\m_5_Coverage\Nooksack30m_LandCover19.asc',
    'Puyallup': r'\Puyallup\Data_Inputs30m\m_5_Coverage\Puyallup30m_LandCover19.asc',
    'Samish': r'\Samish\Data_Inputs30m\m_5_Coverage\Samish30m_LandCover19.asc',
    'Skokomish': r'\Skokomish\Data_Inputs30m\m_5_Coverage\Skokomish30m_LandCover19.asc',
    }

df = pd.read_csv(root_folder+r'\Cell Data Writers.csv', usecols=['Watershed', 'Cell Index'])

for watershed, file in lc_file_dict.items():
    file_path = root_folder + file
    with rasterio.open(file_path) as src:
        lc_file_dict[watershed] = src.read(1)
        
df['Land Cover Code'] = np.nan
    
for idx, row in df.iterrows():
    watershed = row['Watershed']
    cell_index = row['Cell Index']
    if cell_index:
        lc_raster = lc_file_dict[watershed]

        # Convert cell index to 2D row and column
        ncols = lc_raster.shape[1]
        row_idx = cell_index // ncols
        col_idx = cell_index % ncols

        # Retrieve the land cover code
        df.at[idx, 'Land Cover Code'] = lc_raster[int(row_idx), int(col_idx)]

df.to_csv(root_folder + r'\Land Cover Codes.csv', index=False)

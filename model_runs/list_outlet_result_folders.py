"""
Lists all outlet result folders from a VELMA parallel run. Scans the parent
results directory for subfolders (one per outlet/sub-watershed) and writes
their names to OutletList.csv.
"""

import os
import pandas as pd
import numpy as np

# Change directory to parent folder of parallel run results
directory = ('path/to/VELMA_Watersheds/Elwha/Elwha_Working/Results/'
             'MULTI_WA_Hoko30m_ParMulti_800mPRISM_18cover_7June24')

# Change directory to desired output of csv file
out_directory = 'path/to/VELMA_Watersheds/Elwha/Elwha_Working/Analysis/'

# Create list of subfolders
all_entries = os.listdir(directory)
folders = [entry for entry in all_entries if os.path.isdir(os.path.join(directory, entry))]

# Save .csv file with each outlet
out_df = pd.DataFrame({
    'Watershed': folders,
})
out_df.to_csv(f'{out_directory}/OutletList.csv', index=False)

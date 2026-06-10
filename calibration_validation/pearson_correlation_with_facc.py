"""
Computes the Pearson correlation between flow accumulation (facc) and each
chemistry pool raster in a folder, masked to the delineated watershed. Writes
a CSV of r and p values per raster — useful for checking whether end-state
pools are unexpectedly correlated with the flow network.
"""

import rasterio
import numpy as np
from scipy.stats import pearsonr
import os
import pandas as pd

facc_file = 'path/to/VELMA_Watersheds/Huge/Data_Inputs30m/m_1_DEM/Huge30m_Dredge_EEX_facc.asc'
delineation_file = 'path/to/VELMA_Watersheds/Huge/Data_Inputs30m/m_1_DEM/Huge30m_Dredge_EEX_delineated.asc'
raster_folder = 'path/to/VELMA_Watersheds/Huge/Data_Inputs30m/o_10_ChemistryPools/EndState_2000'
out_file = 'path/to/VELMA_Watersheds/Huge/Analysis/facc_correlation.csv'

results = []

with rasterio.open(facc_file) as src:
    facc = src.read(1)
with rasterio.open(delineation_file) as src:
    delineation = src.read(1)
mask = (delineation > 0)

for raster in os.listdir(raster_folder):
    if raster.endswith('.asc'):
        
        with rasterio.open(os.path.join(raster_folder, raster)) as src:
            var = src.read(1)
        r, p = pearsonr(facc[mask], var[mask])
        results.append({'raster': raster, 'r_value': r, 'p_value': p})

df = pd.DataFrame(results)
df.to_csv(out_file, index=False)

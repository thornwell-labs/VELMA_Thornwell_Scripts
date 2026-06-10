"""
Calculates flow-weighted water temperature by marine basin. Weights each
watershed's simulated water surface temperature by its share of the marine
basin's total runoff (using a watershed-to-marine-region lookup) and combines
the results into basin-level temperature series.
"""

import os
import pandas as pd

temperature_col = 'Water_Surface_Temperature(degrees_C)'

input_folder = r"path\to\PSIMF Management\Proof_of_Concept_QC\Full_Results"
output_folder = r"path\to\PSIMF Management\Proof_of_Concept_QC\Full_Results\Flow_Weighted_Temperature"

marine_basin_link_file = r"path\to\PSIMF Management\Marine Basins\VELMA_Watersheds_by_Marine_Region_03312026.csv"
marine_basin_link = pd.read_csv(marine_basin_link_file)

watershed_to_marine_region = (
    marine_basin_link.dropna(subset=["NAME", "MarineRegion"])
    .assign(NAME=lambda df: df["NAME"].astype(str))
    .drop_duplicates(subset=["NAME"])
    .set_index("NAME")["MarineRegion"]
    .to_dict()
)

total_runoff_file = r"path\to\PSIMF Management\Proof_of_Concept_QC\Full_Results\Flow_Weighted_Temperature\marine_basin_runoff_by_date.csv"
total_runoff_df = pd.read_csv(total_runoff_file, parse_dates=['Date'])
total_runoff_df = total_runoff_df.set_index('Date')

for root, dirs, files in os.walk(input_folder):
    for file in files:
        if 'SSM_Results' in file:
            watershed = file.split('_')[0]
            path = os.path.join(root, file)
            watershed_df = pd.read_csv(path, usecols=['Date', temperature_col, 'Runoff(m3/s)'], parse_dates=['Date'])
            watershed_df = watershed_df.set_index('Date')
            
            marine_region = watershed_to_marine_region.get(watershed)
                
            watershed_df['Marine Basin Flow Weighted Temperature (degC)'] = watershed_df[temperature_col] * watershed_df['Runoff(m3/s)'] / total_runoff_df[marine_region]

            out_file = file.replace("SSM_Results", "SSM_Loads")
            watershed_df.to_csv(os.path.join(output_folder, out_file))

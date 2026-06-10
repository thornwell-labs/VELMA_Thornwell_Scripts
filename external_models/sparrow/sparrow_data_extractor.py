"""
Extracts per-watershed total nitrogen predictions from the Puget Sound SPARROW
model output by filtering on NHD COMID, writing one CSV per watershed for
comparison with VELMA loads.
"""

import pandas as pd

data_csv = 'path/to/SPARROW/predict_puget_tn/predict_puget_tn.csv'
watershed_comid_link = 'path/to/SPARROW/psimf_outlet_comid.csv'

df = pd.read_csv(data_csv, usecols=['comid', 'year', 'quarter', 'period', 'flow_cfs', 'station_id', 'PLOAD_TOTAL_ND', 'LOAD'], dtype='str')
watershed_comid_df = pd.read_csv(watershed_comid_link, dtype=str)
watershed_list = watershed_comid_df['Watershed']
comid_list = watershed_comid_df['COMID']

# for watershed, comid in zip(watershed_list, comid_list):
#     filtered_df = df[df['comid'] == comid]
#     filtered_df.to_csv(f'path/to/SPARROW/predict_puget_tn/{watershed}_{comid}_SPARROW.csv', index=False)
#     print(f'Processed {watershed}.')

comid = '24286866'
watershed = 'Quilcene'
filtered_df = df[df['comid'] == comid]
filtered_df.to_csv(f'path/to/SPARROW/predict_puget_tn/{watershed}_{comid}_Ecology_SPARROW.csv', index=False)
print(f'Processed {watershed}.')
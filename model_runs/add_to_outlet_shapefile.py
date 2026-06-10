"""
Merges tabular data (e.g. simulated-to-observed flow fractions) from a CSV
into a VELMA outlet shapefile's attribute table, joining on the outlet cell
index. Useful for mapping calibration metrics in GIS.
"""

import geopandas as gpd
import pandas as pd

# Enter shapefile path and create a geo-dataframe
shapefile_path = 'path/to/VELMA_Watersheds/Elwha/GIS/Vector/parallel_outlets.shp'
gdf = gpd.read_file(shapefile_path)

# Enter data csv path and create a dataframe
csv_path = 'path/to/VELMA_Watersheds/Elwha/Elwha_Working/Analysis/OutletList.csv'
df = pd.read_csv(csv_path)

# Clean up the keys in the df to make sure they match the gdf keys
df['Watershed'] = df['Watershed'].str.replace('Results_', '').astype(int)
gdf['Index'] = gdf['Index'].astype(int)

# Use keys to merge df data into gdf
gdf['SimToObs_F'] = None
gdf = gdf.merge(df, left_on='Index', right_on='Watershed', how='left')
gdf['SimToObs_F'] = gdf['Sim To Obs Fraction']
gdf = gdf.drop(columns=['Sim To Obs Fraction', 'Watershed'])

# Save updated shapefile to specified path
output_path = 'path/to/VELMA_Watersheds/Hoko/GIS/Vector/parallel_outlets.shp'
gdf.to_file(output_path)

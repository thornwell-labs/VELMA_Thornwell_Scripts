"""
Adds human-readable soil names to a SSURGO soil polygon shapefile. Joins the
shapefile's MUSYM codes to names from a pre-processed mapunit lookup table and
writes the names into the attribute table. Includes commented-out code for
producing the lookup table from the raw SSURGO mapunit.txt.
"""

import geopandas as gpd
import pandas as pd

# Pre-process mapunit.txt to be a reasonable lookup table for our values
# with open('path/to/VELMA_Watersheds/Hoko/GIS/Vector/Soils/tabular/mapunit.txt', 'r') as file:
#     lines = file.readlines()
# lines = [s.replace('"', '') for s in lines]
# edited_lines = []
# edited_lines.append(f'MUSYM;NAME')
# for line in lines:
#     columns = line.split('|')
#     columns = columns[0:2]
#     musym, name = columns
#     edited_line = f'{musym+';'+name}'
#     edited_lines.append(edited_line)
#
# with open('path/to/VELMA_Watersheds/Hoko/GIS/Vector/Soils/tabular/mapunit_edited.txt', 'w') as file:
#     for line in edited_lines:
#         file.write(line+'\n')

# Add soil names to shapefile attribute table using mapunit_edited.txt as key
mapunits = pd.read_csv('path/to/VELMA_Watersheds/Hoko/GIS/Vector/Soils/tabular/mapunit_edited.txt', sep=';', dtype=str)
soil_polygons = gpd.read_file('path/to/VELMA_Watersheds/Hoko/GIS/Vector/Soils/spatial/soilmu_a_aoi.shp')
soil_polygon_names = []
for musym in soil_polygons['MUSYM']:
    loc = mapunits.loc[mapunits['MUSYM'] == musym].index[0]
    soil_polygon_names.append(mapunits.loc[loc, 'NAME'])
soil_polygons['Name'] = soil_polygon_names
soil_polygons.to_file('path/to/VELMA_Watersheds/Hoko/GIS/Vector/Soils/spatial/soilmu_a_aoi.shp')
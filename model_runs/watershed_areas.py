"""
Calculates the area (km^2) of every watershed shapefile in a folder.
Reprojects each to NAD83 / UTM 10N if needed, sums polygon areas, and writes
the results to a summary CSV.
"""

import os
import geopandas as gpd
import pandas as pd

# Folder containing shapefiles
folder_path = r"path\to\PSIMF_GIS\Vector\Watersheds"
output_csv = r"path\to\PSIMF_GIS\Vector\Watersheds\watershed_areas.csv"

# EPSG code for the known projection (NAD83 / UTM zone 10N)
known_epsg = 26910

# List to store results
results = []

# Iterate over files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".shp"):
        shapefile_path = os.path.join(folder_path, filename)
        
        # Load the shapefile
        gdf = gpd.read_file(shapefile_path)
        
        # Ensure the projection matches the known EPSG
        if gdf.crs.to_epsg() != known_epsg:
            gdf = gdf.to_crs(epsg=known_epsg)
        
        # Calculate the total area in square kilometers
        total_area_km2 = gdf.geometry.area.sum() / 1e6
        
        # Append to results
        results.append({"Filename": filename, "Area_km2": total_area_km2})

# Create a DataFrame from results and save as CSV
results_df = pd.DataFrame(results)
results_df.to_csv(output_csv, index=False)

print(f"Area calculations saved to {output_csv}")

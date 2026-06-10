"""
Converts a VELMA linear cell index to its (row, column) grid coordinates using
the column count of an .asc raster. Handy for locating a cell index on a map.
"""

import rasterio

def linear_index_to_row_col(file_path, index):
    with rasterio.open(file_path) as src:
        ncols = src.width  # Automatically gets the number of columns
        row = index // ncols
        col = index % ncols
        return row, col

# Example usage
file_path = r"path\to\VELMA_Watersheds\Samish\Data_Inputs30m\m_1_DEM\Samish30m_DredgeMask_EEX.asc"
# index = 96753  # Replace with your linear index
indices = [8219]

for index in indices:
    row, col = linear_index_to_row_col(file_path, index)
    y, x = row, col
    print(f"Linear index {index} corresponds to grid coordinates (X: {x}, Y: {y})")

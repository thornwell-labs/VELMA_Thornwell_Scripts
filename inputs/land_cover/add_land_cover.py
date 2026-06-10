"""
Adds a land cover class (e.g. pasture) from an NLCD raster into an existing
VELMA land cover .asc file. The NLCD raster is resampled to match the .asc
grid, then cells flagged in the NLCD data overwrite the corresponding land
cover cells. Requires resample_raster.py (see utilities/).
"""

import rasterio
from rasterio.crs import CRS
from resample_raster import resample_raster

# Set these file paths and names before running
nlcd_path = 'path/to/PSIMF_GIS/Raster/pasture_land_cover.tif'
watershed_name = "Skokomish"
nlcd_resampled_path = f'path/to/PSIMF_GIS/Raster/{watershed_name}_NLCD.tif'
land_cover_path = f'path/to/VELMA_Watersheds/Skokomish/Data_Inputs30m/m_5_Coverage/{watershed_name}_LandCover18.asc'
output_path = f'path/to/VELMA_Watersheds/Skokomish/Data_Inputs30m/m_5_Coverage/{watershed_name}30m_LandCover19.asc'

# Should not need to edit anything below this line

def add_pasture(nlcd_path, nlcd_resampled_path, land_cover_path, output_path):
    # Read in the land cover data
    with rasterio.open(land_cover_path) as asc:
        land_cover_data = asc.read(1)
        if asc.crs is None:
            land_cover_crs = CRS.from_string("EPSG:26910")
        else:
            land_cover_crs = asc.crs
        land_cover_transform = asc.transform
        land_cover_nodata = asc.nodata

    # Resample the NLCD data and save the resampled raster (can delete afterwards)
    resample_raster(nlcd_path, land_cover_path, nlcd_resampled_path, nodata=land_cover_nodata, method='nearest')

    # Read in the resampled NLCD data
    with rasterio.open(nlcd_resampled_path) as tif:
        if tif.crs is None:
            nlcd_crs = CRS.from_string("EPSG:26910")
        else:
            nlcd_crs = tif.crs
        nlcd_data = tif.read(1)
        nlcd_transform = tif.transform

    # These checks guarantee that the transform, shape and projection of the .asc and NLCD data are identical
    if land_cover_transform != nlcd_transform or land_cover_data.shape != nlcd_data.shape:
        raise ValueError("The transform and/or shapes of the NLCD and land cover rasters do not match. Reprojection or alignment is required.")
    if land_cover_crs.to_epsg() != 26910:
        raise ValueError(f"Land cover .asc file CRS is {land_cover_crs}, not EPSG 26910")
    if nlcd_crs.to_epsg() != 26910:
        raise ValueError(f"NLCD .tif file CRS is {nlcd_crs}, not EPSG 26910")

    # Iterate over the land cover data and find pasture cells
    rows, cols = land_cover_data.shape
    for row in range(rows):
        for col in range(cols):
            if land_cover_data[row, col] != land_cover_nodata:  # Ensure cell is not nodata
                # Check corresponding value in NLCD data
                if nlcd_data[row, col] == 1:  # Binary raster: 1 indicates land cover ID 81
                    land_cover_data[row, col] = 81  # Update land cover value

    # Copy metadata from the original land cover data
    land_cover_meta = asc.meta.copy()
    land_cover_meta.update(dtype=rasterio.int32, nodata=land_cover_nodata)

    # Write the new land cover data to a file
    with rasterio.open(output_path, "w", **land_cover_meta) as dst:
        dst.write(land_cover_data, 1)

    print(f"Updated land cover raster saved to {output_path}")

add_pasture(nlcd_path, nlcd_resampled_path, land_cover_path, output_path)

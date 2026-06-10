""" 
Accepts SOLUS 100m data .tif file and manipulates to match the extent, grid configuration,
and projection of an input .asc file (suggest using the watershed DEM file).
Output file is .asc grid
"""

import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np
from pyproj import CRS


# Define SOLUS data as a dictionary. The key is the desired file name and the value is the file path of the input data
# Can process multiple files using this dictionary
SOLUS_data = {'nitrogen_reduction_fractions_Sammamish': 'path/to/SOLUS/nitrogen_reduction_fractions.tif',
              }

# Define the desired .asc file shape
asc_data = ('path/to/VELMA_Watersheds/Sammamish/Data_Inputs30m/m_1_DEM/Sammamish_DredgeMask_EEX.asc')

# Define desired output folder of clipped SOLUS data
out_path = 'path/to/VELMA_Watersheds/Sammamish/Data_Inputs30m/o_10_ChemistryPools/SOLUS_HumusN/'

# Define projections of the desired .asc and the SOLUS data (tif_crs)
asc_crs = CRS.from_epsg(26910)
tif_crs = CRS.from_epsg(26910)

# ----- Shouldn't need to edit anything below this line ------


# Resample the SOLUS 100m data to match the cell resolution and location of the DEM .asc file
def resample_tif_to_match_asc(tif_file, asc_file, output_asc, asc_crs, tif_crs):

    # Open the .asc file to get its transform and shape (extent, resolution)
    with rasterio.open(asc_file) as asc_src:
        asc_transform = asc_src.transform
        asc_width = asc_src.width
        asc_height = asc_src.height

    # Open the .tif file to resample
    with rasterio.open(tif_file) as tif_src:
        tif_data = tif_src.read(1)  # Reading the first band
        tif_meta = tif_src.meta.copy()

        # Define the output array for the resampled data
        resampled_data = np.empty((asc_height, asc_width), dtype=tif_data.dtype)

        # Update the metadata for the resampled .tif
        tif_meta.update({
            'driver': 'AAIGrid',
            'height': asc_height,
            'width': asc_width,
            'transform': asc_transform,
            'crs': asc_crs.to_proj4(),
            'nodata': -9999
        })

        # Perform the resampling
        reproject(
            source=tif_data,
            destination=resampled_data,
            src_transform=tif_src.transform,
            src_crs=tif_crs.to_proj4(),  # Source CRS
            dst_transform=asc_transform,
            dst_crs=asc_crs.to_proj4(),  # Destination CRS
            resampling=Resampling.nearest,  # Can use nearest, bilinear, etc.
            dst_nodata=-9999
        )

        # Save the resampled .tif
        with rasterio.open(output_asc, 'w', **tif_meta) as dst:
            dst.write(resampled_data, 1)


for var, tif_file in SOLUS_data.items():
    output_asc = out_path+var+'.asc'
    resample_tif_to_match_asc(tif_file, asc_data, output_asc, asc_crs, tif_crs)

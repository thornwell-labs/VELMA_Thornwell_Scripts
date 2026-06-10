"""
Builds a GDAL VRT for a land cover raster that embeds human-readable class
names as metadata. Reads a key table CSV mapping VELMA land cover codes to
names so GIS software can display labels instead of numeric codes.
"""

from osgeo import gdal
import pandas as pd
import xml.etree.ElementTree as ET

# Open raster full of land cover codes
raster_path = "path/to/PSIMF_GIS/Raster/NLCD_LEMMA_LandCover30m_PugetSound.tif"
raster_lc = gdal.Open(raster_path, gdal.GA_Update)
band = raster_lc.GetRasterBand(1)

# Get raster dimensions
raster_x_size = raster_lc.RasterXSize
raster_y_size = raster_lc.RasterYSize

# Get raster coordinate system data
geo_transform = raster_lc.GetGeoTransform()
projection = raster_lc.GetProjection()

# Create dictionary relating land cover codes to the name of the land cover type
key_table_path = "path/to/PSIMF_GIS/LandCoverKey.csv"
key_df = pd.read_csv(key_table_path)
land_cover_dict = pd.Series(key_df['Land Cover'].values, index=key_df['VELMA Code']).to_dict()

# Create VRT to associate with raster, use geotransform and projection from original raster

vrt = ET.Element("VRTDataset", rasterXSize=str(raster_x_size), rasterYSize=str(raster_y_size))
geo_transform_element = ET.SubElement(vrt, "GeoTransform")
geo_transform_element.text = ",".join(map(str, geo_transform))
srs = ET.SubElement(vrt, "SRS")
srs.text = projection

# Add data band
vrt_band = ET.SubElement(vrt, "VRTRasterBand", dataType=gdal.GetDataTypeName(band.DataType), band="1")

# Create source filename
source = ET.SubElement(vrt_band, "SimpleSource")
source_filename = ET.SubElement(source, "SourceFilename")
source_filename.text = raster_path
source_filename.set("relativeToVRT", "1")
source_band = ET.SubElement(source, "SourceBand")
source_band.text = "1"
source_properties = ET.SubElement(source, "SourceProperties",
                                  RasterXSize=str(raster_x_size),
                                  RasterYSize=str(raster_y_size),
                                  DataType=gdal.GetDataTypeName(band.DataType),
                                  BlockXSize=str(band.GetBlockSize()[0]),
                                  BlockYSize=str(band.GetBlockSize()[1]))

# Add metadata
metadata = ET.SubElement(vrt_band, "Metadata")
for value, name in land_cover_dict.items():
    item = ET.SubElement(metadata, "MDI", key=str(value))
    item.text = name

# Create vrt file
vrt_path = raster_path.replace('.tif', '.vrt')
tree = ET.ElementTree(vrt)
tree.write(vrt_path, encoding="utf-8", xml_declaration=True)

print(f"VRT file created at: {vrt_path}")
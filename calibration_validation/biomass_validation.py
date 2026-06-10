"""
Validates VELMA-simulated biomass against an observed conifer biomass raster.
Extracts co-located biomass, stand age, humus, soil moisture, and elevation
values, then explores their relationships with regression and plots.
"""

import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm

# File paths
root_folder = 'path/to/VELMA_Watersheds/Samish/Results/MULTI_WA_Samish30m_21March2025_Hyak/'
biomass_file = root_folder+'Samish_conifer_biomass_2008.tif'
age_file = root_folder+'Spatial_CoverAge_ALL_1_2008_1.asc'
humus_file = root_folder+'Spatial_HUMUS_ALL_1_2008_1.asc'
soil_moisture_file = root_folder+'Spatial_WATER_STORED_ALL_1_2008_1.asc'
elevation_file = 'path/to/VELMA_Watersheds/Samish/Data_Inputs30m/m_1_DEM/Samish30m_DredgeMask_EEX.asc'
output_folder = 'path/to/VELMA_Watersheds/Samish/Analysis/21Mar2025'

# Open and read the raster files
with rasterio.open(biomass_file) as src_biomass:
    biomass = src_biomass.read(1)  # read the first band

with rasterio.open(age_file) as src_age:
    age = src_age.read(1)  # read the first band
    
with rasterio.open(humus_file) as src_humus:
    humus = src_humus.read(1)  # read the first band

with rasterio.open(soil_moisture_file) as src_soil:
    soil_moisture = src_soil.read(1)  # read the first band
    
with rasterio.open(elevation_file) as src_elevation:
    elevation = src_elevation.read(1)  # read the first band

# Create a mask: valid data where biomass is greater than zero
mask = biomass > 0

# Extract the valid values from both arrays
valid_biomass = biomass[mask]
valid_age = age[mask]
valid_humus = humus[mask]
valid_soil_moisture = soil_moisture[mask]
valid_elevation = elevation[mask]

# Create a DataFrame with the valid paired data
df = pd.DataFrame({
    'Age': valid_age,
    'Biomass': valid_biomass,
    'Humus': valid_humus,
    'Soil_Moisture': valid_soil_moisture,
    'Elevation': valid_elevation
})

# Save the data to a CSV file
csv_filename = f'{output_folder}/biomass_data.csv'
df.to_csv(csv_filename, index=False)
print(f"CSV file saved as {csv_filename}")

# Create a scatter plot: Age (x-axis) vs Biomass (y-axis)
plt.figure(figsize=(8, 6))
plt.scatter(df['Age'], df['Biomass'], alpha=0.5, edgecolor='k')
plt.xlabel('Age (years)')
plt.ylabel('Biomass (g/m2)')
plt.title('Age vs Biomass')
plt.grid(True)
plt.tight_layout()

# Save the plot to a file
plot_filename = f'{output_folder}/age_biomass_plot.png'
plt.savefig(plot_filename)
print(f"Plot saved as {plot_filename}")

# Display the plot
plt.show()

# Create a multiple regression model to test which predictor variables have the strongest effect on biomass
X = np.column_stack((valid_age, valid_humus, valid_soil_moisture, valid_elevation))
y = valid_biomass
X = sm.add_constant(X)
model = sm.OLS(y, X).fit()
print(model.summary())

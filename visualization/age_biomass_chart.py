"""
Plots conifer biomass against stand age from co-located biomass and age
rasters, pairing valid cells (biomass > 0) and exporting the paired data to
CSV for an age-biomass relationship chart.
"""

import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# File paths
biomass_file = 'path/to/PSIMF_GIS/Raster/samish_deep_conifer_biomass.tif'
age_file     = 'path/to/PSIMF_GIS/Raster/samish_conifer_age.tif'

# Open and read the raster files
with rasterio.open(biomass_file) as src_biomass:
    biomass = src_biomass.read(1)  # read the first band

with rasterio.open(age_file) as src_age:
    age = src_age.read(1)  # read the first band

# Create a mask: valid data where biomass is greater than zero
mask = biomass > 0

# Extract the valid values from both arrays
valid_biomass = biomass[mask]
valid_age     = age[mask]

# Create a DataFrame with the valid paired data
df = pd.DataFrame({
    'Age': valid_age,
    'Biomass': valid_biomass
})

# Save the data to a CSV file
csv_filename = 'path/to/VELMA_Watersheds/Samish/Analysis/deep_age_biomass_data.csv'
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
plot_filename = 'path/to/VELMA_Watersheds/Samish/Analysis/deep_age_biomass_plot.png'
plt.savefig(plot_filename)
print(f"Plot saved as {plot_filename}")

# Display the plot
plt.show()

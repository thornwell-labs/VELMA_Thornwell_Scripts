"""
Accepts a restrictive depth .tif file that should already be clipped to your project area.
Returns the data clustered according to a K-Means algorithm.
"""

import numpy as np
import rasterio
from sklearn.cluster import KMeans


# Specify these paths
restrictive_depth_file = 'path/to/SOLUS/resdept_Puget_Sound_proj.tif'  # Path to the clipped restrictive depth .tif file
num_clusters = 3  # Specify the number of clusters for the K-Means algorithm
write_tif_file = True  # True if you want the output .tif data
out_file_path = ''  # Path to the output .tif file

# ----- Shouldn't need to edit anything below this line -----


with rasterio.open(restrictive_depth_file) as src:
    data = src.read(1)

# Handle NoData values by masking them
data = np.ma.masked_equal(data, src.nodata)

# Turn the values into a 1D array
values = data.compressed()

# Make sure there are no NaN values in the input to KMeans
values = values[~np.isnan(values)]  # Remove any remaining NaN values

# Turn the values into a 1D array
values = values.reshape(-1, 1)

# Apply k-means with 3 clusters
kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(values)

# Print the mean of each group (cluster center)
print("Mean of each group:", kmeans.cluster_centers_.flatten())

# Initialize dictionaries to store the ranges
cluster_ranges = {}

# Find the minimum and maximum values for each cluster
for cluster_num in range(kmeans.n_clusters):
    cluster_data = values[kmeans.labels_.flatten() == cluster_num].flatten()
    min_value = np.min(cluster_data)
    max_value = np.max(cluster_data)
    cluster_ranges[cluster_num] = (min_value, max_value)

# Print the value ranges for each cluster
for cluster_num, (min_value, max_value) in cluster_ranges.items():
    print(f"Cluster {cluster_num}: Min = {min_value}, Max = {max_value}")

# Print the size of each cluster
cluster_sizes = np.bincount(kmeans.labels_)
print("Size of each cluster:", cluster_sizes)

# Create an array for the labels with the same shape as the original data
labels = np.full(data.shape, -9999, dtype=int)  # Initialize with -9999 for NoData cells

# Classify each pixel based on the cluster ranges
for cluster_num, (min_value, max_value) in cluster_ranges.items():
    cluster_mask = (data >= min_value) & (data <= max_value)
    labels[cluster_mask] = cluster_num

if write_tif_file:
    with rasterio.open(
        out_file_path,
        'w',
        driver='GTiff',
        height=src.height,
        width=src.width,
        count=1,
        dtype=rasterio.int32,
        crs=src.crs,
        transform=src.transform,
        nodata=-9999
    ) as dst:
        dst.write(labels, 1)

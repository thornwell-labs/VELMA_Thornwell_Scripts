"""
Clusters PSIMF watersheds by their runoff-driver correlation signatures using
k-means. Standardizes the per-watershed r-value columns from the runoff driver
analysis and groups watersheds into clusters with similar dominant drivers.
"""

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

input_file_path = r"path\to\PSIMF Management\Proof_of_Concept_QC\Runoff Driver Analysis_2010-2049.csv"

df = pd.read_csv(input_file_path)

# Select only R-value columns
r_cols = [c for c in df.columns if 'r-value' in c.lower()]
r_df = df[r_cols].copy()

# Fill all missing rows with zeroes using numpy
r_df = r_df.fillna(0.0)

# Standardize
scaler = StandardScaler()
X = scaler.fit_transform(r_df)

# Perform k-means clustering
k = 5
kmeans = KMeans(
    n_clusters=k,
    n_init=50,
    random_state=42
)

clusters = kmeans.fit_predict(X)

# Attach results back to dataframe
df['kmeans_group_r_only'] = clusters

# Save results
output_file = r"path\to\PSIMF Management\Proof_of_Concept_QC\Runoff_Driver_kmeans_2010-2049.csv"
df.to_csv(output_file, index=False)

# --------------------------------
# Extract cluster centroids
# --------------------------------
centroids_std = kmeans.cluster_centers_

# Transform back to original r-value scale
centroids = scaler.inverse_transform(centroids_std)

centroid_df = pd.DataFrame(
    centroids,
    columns=r_cols
)
centroid_df['cluster'] = centroid_df.index

print(centroid_df)


plt.figure(figsize=(10, 5))

for i in range(k):
    plt.plot(
        r_cols,
        centroid_df.loc[i, r_cols],
        marker='o',
        label=f'Cluster {i}'
    )

plt.axhline(0, linestyle='--', linewidth=0.8)
plt.xticks(rotation=45, ha='right')
plt.ylabel('Mean Pearson r')
plt.title('Cluster centroid runoff–driver patterns')
plt.legend()
plt.tight_layout()
plt.show()

clusters = sorted(df['kmeans_group_r_only'].unique())

plt.figure()

for cluster in clusters:
    subset = df[df['kmeans_group_r_only'] == cluster]
    plt.scatter(
        subset['Mean Centroid Northing'],
        subset['Mean Elevation'],
        label=f'Cluster {cluster}'
    )

for _, row in df.iterrows():
    plt.annotate(
        row['Watershed'],
        (row['Mean Centroid Northing'], row['Mean Elevation']),
        xytext=(4, 4),
        textcoords='offset points',
        fontsize=8
    )

plt.xlabel('Centroid northing (m)')
plt.ylabel('Mean elevation (m)')
plt.title('Clusters in geographic context')
plt.legend(title='K-means Group')
plt.show()

plt.figure()

for cluster in clusters:
    subset = df[df['kmeans_group_r_only'] == cluster]
    plt.scatter(
        subset['2019 Percent Forest'],
        subset['2020 snow/precip'],
        label=f'Cluster {cluster}'
    )

for _, row in df.iterrows():
    plt.annotate(
        row['Watershed'],
        (row['2019 Percent Forest'], row['2020 snow/precip']),
        xytext=(4, 4),
        textcoords='offset points',
        fontsize=8
    )

plt.xlabel('2019 Percent Forest')
plt.ylabel('2020 snow/precip')
plt.title('Model drivers of clusters')
plt.legend(title='K-means Group')
plt.show()

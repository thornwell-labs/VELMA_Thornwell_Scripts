"""
Downsamples a VELMA land cover .asc grid by majority rule while preserving the
original distribution of land cover classes. After the initial majority-rule
resample, iteratively reassigns borderline mixed cells so each class's percent
share stays within tolerance of the full-resolution map, then writes the
adjusted .asc file.
"""

# Algorithm outline:
# 1) Import land cover .asc file as a raster
# 2) Perform simple resampling by majority rule
# 3) Calculate the histogram (as percentage) in the original, non-resampled version and print out
# 4) Calculate the histogram (as percentage) in the resampled version and print out
# 5) For each land cover type, find the difference in percentages
# 6) List the land cover types where the resampled land cover type is outside the tolerance
# 7) For each land cover type in the list from step 6, calculate the number of integer cells (rounded down) that need to change in the resampled version to match the non-resampled version and print out
    # 8) Record resampled cell ID's (either by index or position) that had "mixed" land cover types containing the land cover type, but not containing majority of that land cover type
        # for example - the resampled larger cell had 9 sub-cells, and 4 of them were the land cover type in question. Should be recorded with an identifier for the resampled cell ID and the number 4.
        # if the resampled larger cell had 9 sub-cells (downscaling factor is 3), then resampled cells with >5 of the land cover type should be ignored
    # 9) Sort the cell ID's by share of land cover type in question
    # 10) Keep the cell ID's sorted by their share of the land cover type, but within each integer group, randomize to make sure they are not sorted by the cell identifiers
    # 11) Cut the list of cell ID's so its length matches the number calculated in step 7
    # 12) Re-assign this list of cell ID's to the land cover type in question
    # 13) Calculate the new histogram (as percentage) of the original and new resampled land cover version and check for tolerance and number of iterations
    # 14) Repeat the loop until max iterations is achieved or all land cover types are within tolerance
# 15) Save the new resampled land cover .asc file with the new land cover assignments

import numpy as np
import rasterio
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap

land_cover_path = 'path/to/VELMA_Watersheds/Huge/Data_Inputs30m/m_5_Coverage/Huge30m_LandCover19.asc'
downscale_factor = 3
output_path = f'path/to/VELMA_Watersheds/Huge/Data_Inputs30m/m_5_Coverage/Huge30m_LandCover19_resampled_{downscale_factor}_test.asc'

rng = np.random.default_rng(seed=42)  # Random seed for reproducibility

# Load raster
with rasterio.open(land_cover_path) as src:
    original_data = src.read(1)
    profile = src.profile
    transform = src.transform
    nodata = src.nodata

# Resample by majority rule
def resample_majority(data, factor, nodata_val):
    rows, cols = data.shape
    out_rows, out_cols = rows // factor, cols // factor
    resampled = np.full((out_rows, out_cols), nodata_val, dtype=data.dtype)

    for i in range(out_rows):
        for j in range(out_cols):
            block = data[i*factor:(i+1)*factor, j*factor:(j+1)*factor]
            block_flat = block.flatten()
            block_flat = block_flat[block_flat != nodata_val]
            if block_flat.size > 0:
                majority = Counter(block_flat).most_common(1)[0][0]
                resampled[i, j] = majority
    return resampled

resampled_data = resample_majority(original_data, downscale_factor, nodata)

# Helper function to compute histogram for land cover distribution
def compute_histogram(data, nodata_val):
    flat = data.flatten()
    valid = flat[flat != nodata_val]
    total = len(valid)
    counts = Counter(valid)
    return {k: v / total * 100 for k, v in counts.items()}

original_hist = compute_histogram(original_data, nodata)
resampled_hist = compute_histogram(resampled_data, nodata)

# print("Original Land Cover Histogram (%):")
# for lc, pct in sorted(original_hist.items()):
#     print(f"  Land Cover {int(lc)}: {pct:.1f}%")

# print("Resampled Land Cover Histogram (%):")
# for lc, pct in sorted(resampled_hist.items()):
#     print(f"  Land Cover {int(lc)}: {pct:.1f}%")

# Get statistics for each subcell
def get_subcell_stats(original, resampled_shape, factor, nodata_val):
    stats = {}  # {land_cover_type: list of (count, (i, j))}
    rows, cols = resampled_shape
    for i in range(rows):
        for j in range(cols):
            block = original[i*factor:(i+1)*factor, j*factor:(j+1)*factor]
            flat = block.flatten()
            flat = flat[flat != nodata_val]
            if len(flat) == 0:
                continue
            sub_counts = Counter(flat)
            majority = max(sub_counts, key=sub_counts.get)
            for lc, count in sub_counts.items():
                if lc != majority:
                    stats.setdefault(lc, []).append((count, (i, j)))
    return stats

subcell_stats = get_subcell_stats(original_data, resampled_data.shape, downscale_factor, nodata)

# Rules for rebalancing iteratively
max_iterations = 10
tolerance = 0.1  # percent tolerance for histogram match
max_reassignments_per_cell = 3  # max number of times a cell can be overwritten

# Track how many times a cell has been reassigned
reassignment_counts = np.zeros(resampled_data.shape, dtype=int)

corrected_data = resampled_data.copy()

for iteration in range(max_iterations):
    print(f"\nIteration {iteration+1}")

    corrected_hist = compute_histogram(corrected_data, nodata)

    # Calculate differences (original - corrected)
    diffs = {k: original_hist.get(k, 0) - corrected_hist.get(k, 0) for k in original_hist}
    underrepresented = {k: v for k, v in diffs.items() if v > tolerance}

    print(f"Underrepresented land cover types (>{tolerance}%): {underrepresented}")

    # Stop if all within tolerance
    if not underrepresented:
        print("Histogram proportions are within tolerance. Stopping iterations.")
        break

    # Total number of valid cells
    total_cells = np.count_nonzero(corrected_data != nodata)

    # For each land cover type that is underrepresented, compute cells needed
    to_assign_counts = {
        lc: int(np.ceil(v / 100 * total_cells))
        for lc, v in underrepresented.items()
    }
    print("Cells needed to reassign per land cover type:", to_assign_counts)

    # For each land cover type, reassign cells (allow overwrites)
    for lc_type, needed in to_assign_counts.items():
        candidates = subcell_stats.get(lc_type, [])
        # Filter out cells already reassigned too often
        candidates = [(count, coord) for count, coord in candidates if reassignment_counts[coord] < max_reassignments_per_cell]

        # Sort by minority count descending
        candidates.sort(key=lambda x: x[0], reverse=True)

        # Group by count to randomize within same-count groups
        grouped = {}
        for count, coord in candidates:
            grouped.setdefault(count, []).append(coord)

        sorted_coords = []
        for count in sorted(grouped.keys(), reverse=True):
            group = grouped[count]
            rng.shuffle(group)
            sorted_coords.extend(group)

        # Select up to needed number of cells
        selected = sorted_coords[:needed]

        print(f"Assigning {len(selected)} cells to land cover {lc_type}")

        for i, j in selected:
            corrected_data[i, j] = lc_type
            reassignment_counts[i, j] += 1

# Final histogram
final_hist = compute_histogram(corrected_data, nodata)
# print("\nFinal corrected histogram:")
# for lc, pct in sorted(final_hist.items()):
#     print(f"  Land Cover {int(lc)}: {pct:.1f}%")

# -- Save output raster --
new_profile = profile.copy()
new_profile.update({
    'height': corrected_data.shape[0],
    'width': corrected_data.shape[1],
    'transform': rasterio.Affine(
        transform.a * downscale_factor, transform.b, transform.c,
        transform.d, transform.e * downscale_factor, transform.f
    )
})

with rasterio.open(output_path, 'w', **new_profile) as dst:
    dst.write(corrected_data, 1)

print(f"\nResampled land cover saved to: {output_path}")


# Function to plot side-by-side pie charts of histograms
def plot_histograms(original_hist, resampled_hist, corrected_hist):
    fig, axs = plt.subplots(1, 3, figsize=(20, 7))
    histograms = [original_hist, resampled_hist, corrected_hist]
    titles = ["Original Land Cover", "Resampled (Majority Rule)", "Corrected (Proportional)"]

    all_lc_types = sorted(set().union(*[hist.keys() for hist in histograms]))
    num_types = len(all_lc_types)

    cmap = get_cmap('tab20', num_types)
    color_map = {lc: cmap(i) for i, lc in enumerate(all_lc_types)}

    for ax, hist, title in zip(axs, histograms, titles):
        full_hist = {lc: hist.get(lc, 0.0) for lc in all_lc_types}
        labels = [str(lc) for lc in all_lc_types]
        sizes = list(full_hist.values())
        colors = [color_map[lc] for lc in all_lc_types]

        ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct=lambda p: f'{p:.1f}%' if p >= 1 else '',
            startangle=90
        )
        ax.axis('equal')
        ax.set_title(title)

    plt.tight_layout()
    plt.show()

# Plot histograms after processing
plot_histograms(original_hist, resampled_hist, final_hist)

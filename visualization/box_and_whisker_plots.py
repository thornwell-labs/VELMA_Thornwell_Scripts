"""
Creates box-and-whisker plots summarizing the penumbra (riparian shading)
analysis, including outlier-trimmed means and R^2 improvement data, to compare
model performance across watersheds with and without the penumbra feature.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def mean_excluding_outliers(series):
    """Return mean of a Series after removing 1.5×IQR outliers."""
    s = series.dropna()
    if s.empty:
        return np.nan

    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    s_no_outliers = s[(s >= lower) & (s <= upper)]
    if s_no_outliers.empty:
        return np.nan

    return s_no_outliers.mean()


plt.rcParams.update({"font.size": 12})
plt.rc("figure", titlesize=14)

data_file = r"path\to\PSIMF Management\Penumbra_Analysis\Summary_for_Plot.csv"
r2_data_file = r"path\to\PSIMF Management\Penumbra_Analysis\R2_Improvements.csv"

# ===========================
# Temperature boxplots (no mean labels)
# ===========================
df = pd.read_csv(data_file)

labels = ["Annual", "Spring", "Summer", "Fall", "Winter"]

cols_with_penumbra = [
    "Annual_Tavg_SimMinusObs_Diff_with_Penumbra",
    "Spring_Tavg_SimMinusObs_Diff_with_Penumbra",
    "Summer_Tavg_SimMinusObs_Diff_with_Penumbra",
    "Fall_Tavg_SimMinusObs_Diff_with_Penumbra",
    "Winter_Tavg_SimMinusObs_Diff_with_Penumbra",
]

cols_without_penumbra = [
    "Annual_Tavg_SimMinusObs_Diff_without_Penumbra",
    "Spring_Tavg_SimMinusObs_Diff_without_Penumbra",
    "Summer_Tavg_SimMinusObs_Diff_without_Penumbra",
    "Fall_Tavg_SimMinusObs_Diff_without_Penumbra",
    "Winter_Tavg_SimMinusObs_Diff_without_Penumbra",
]

fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
positions = range(len(labels))

# Without penumbra
df[cols_without_penumbra].boxplot(ax=axes[0])
axes[0].set_title("Sim − Obs Mean Temp without Penumbra")
axes[0].set_ylabel("Temperature difference (deg C)")
axes[0].set_xticks(positions)
axes[0].set_xticklabels(labels, rotation=45)

# With penumbra
df[cols_with_penumbra].boxplot(ax=axes[1])
axes[1].set_title("Sim − Obs Mean Temp with Penumbra")
axes[1].set_xticks(positions)
axes[1].set_xticklabels(labels, rotation=45)

for ax in axes:
    ax.grid(True, axis="y")
    ax.grid(False, axis="x")

plt.tight_layout()
plt.savefig(r"path\to\PSIMF Management\Penumbra_Analysis\penumbra_results_box_whisker.png")
plt.show()
plt.close()

# ===========================
# R² boxplots with mean labels (excluding outliers)
# ===========================
df_r2 = pd.read_csv(r2_data_file)

# Helper to annotate a single-column boxplot
def annotate_r2_mean(ax, series, x_pos=1, y_offset_frac=0.02, fmt="{:.3f}"):
    """Annotate mean (excluding outliers) for a single box at x_pos."""
    mean_val = mean_excluding_outliers(series)
    if np.isnan(mean_val):
        return

    ymin, ymax = ax.get_ylim()
    dy = (ymax - ymin) * y_offset_frac

    ax.text(
        x_pos,
        mean_val + dy,
        fmt.format(mean_val),
        ha="center",
        va="bottom",
        fontsize=10,
        color="black",
    )

# R² without penumbra
fig, ax = plt.subplots(figsize=(8, 10))
df_r2[["R2 Without Penumbra"]].boxplot(ax=ax)
ax.set_title("Temperature Model Fitness Without Penumbra")
ax.set_ylabel(r"$R^2$")
ax.grid(True, axis="y")
ax.grid(False, axis="x")

annotate_r2_mean(ax, df_r2["R2 Without Penumbra"], x_pos=1, y_offset_frac=0.005)

plt.tight_layout()
plt.savefig(r"path\to\PSIMF Management\Penumbra_Analysis\r2_without_penumbra.png")
plt.show()
plt.close()

# R² with penumbra
fig, ax = plt.subplots(figsize=(8, 10))
df_r2[["R2 With Penumbra"]].boxplot(ax=ax)
ax.set_title("Temperature Model Fitness With Penumbra")
ax.set_ylabel(r"$R^2$")
ax.grid(True, axis="y")
ax.grid(False, axis="x")

annotate_r2_mean(ax, df_r2["R2 With Penumbra"], x_pos=1, y_offset_frac=0.005)

plt.tight_layout()
plt.savefig(r"path\to\PSIMF Management\Penumbra_Analysis\r2_with_penumbra.png")
plt.show()
plt.close()

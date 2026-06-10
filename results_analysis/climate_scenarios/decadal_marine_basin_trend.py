"""
Summarizes decadal trends in a load variable (e.g. annual DOC load) aggregated
by marine basin. Groups PSIMF watersheds into their marine regions, totals the
variable per decade, and reports percent differences between decades.
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

folder_path = r"path\to\PSIMF Management\Proof_of_Concept_QC\Full_Results\Loads"
out_folder = 'path/to/PSIMF Management/Proof_of_Concept_QC/Decadal_Trend_Analysis'

variable_of_interest = 'DOC_Loss(kg/d)'
variable_name = 'Annual DOC Load'

# Create dictionary linking watershed and marine region using marine basins file
marine_region_file = r"path\to\PSIMF Management\Marine Basins\VELMA_Watersheds_by_Marine_Region_03312026.csv"
marine_region_df = pd.read_csv(marine_region_file)
marine_region_dict = (
    marine_region_df
    .groupby("MarineRegion")["NAME"]
    .apply(list)
    .to_dict()
)

results_df = pd.DataFrame(columns=["Marine Region", 2010, 2020, 2030, 2040, "Percent Difference"])

for marine_region, watershed_list in marine_region_dict.items():
    full_df = None
    # Create a dataframe and populate it with the total from within that marine basin
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if 'SSM_Loads' in file:
                # Check to make sure the watershed is within this marine region
                watershed_name = file.split('_')[0]
                if watershed_name in watershed_list:
                    watershed_df = pd.read_csv(os.path.join(folder_path, file), usecols=[variable_of_interest, 'Date'], parse_dates=['Date'])
                    if full_df is None:
                        full_df = watershed_df
                    else:
                        full_df[variable_of_interest] = full_df[variable_of_interest] + watershed_df[variable_of_interest]  # This should create values indexed by date if they don't already exist. Otherwise, add the values to the existing values.

    # Add the year to the data and filter to past 2010
    full_df["Year"] = full_df["Date"].dt.year
    full_df = full_df[full_df["Year"] >= 2010]
    
    # Filter additional years as desired
    year_range = list(range(2010, 2050))
    full_df = full_df[full_df["Year"].isin(year_range)]
    
    # Add the decade to the data
    full_df["Decade"] = (full_df["Year"] // 10) * 10

    # Average within each year
    year_totals = (
        full_df.groupby(["Year", "Decade"])[variable_of_interest]
        .sum()
        .reset_index()
    )

    # Average those yearly totals across each decade
    decade_summary = (
        year_totals.groupby(["Decade"])[variable_of_interest]
        .mean()
    )
    
    val_2010 = decade_summary.get(2010, pd.NA)
    val_2020 = decade_summary.get(2020, pd.NA)
    val_2030 = decade_summary.get(2030, pd.NA)
    val_2040 = decade_summary.get(2040, pd.NA)
    pct_diff = ((val_2040 - val_2020) / val_2020) * 100
    
    new_row = pd.DataFrame([{
        "Marine Region": marine_region,
        2010: val_2010,
        2020: val_2020,
        2030: val_2030,
        2040: val_2040,
        "Percent Difference": pct_diff
    }])

    results_df = pd.concat([results_df, new_row], ignore_index=True)

# After all the results have been compiled, save the dataframe
results_df.to_csv(f'{out_folder}/{variable_name}_decadal_by_marine_region.csv', index=False)

# Bar chart of percent difference by marine basin
plot_df = results_df.set_index("Marine Region")
ax = plot_df["Percent Difference"].plot(kind="bar", color="steelblue", edgecolor="black", figsize=(8, 5))
plt.axhline(0, color="black", linewidth=1)
ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.0f}%"))
plt.ylabel("Percent Difference")
plt.xlabel("Marine Region")
plt.title(f"{variable_name} Percent Difference by Marine Region: 2040s vs 2020s")
plt.tight_layout()
plt.savefig(f"{out_folder}/{variable_name}_percent_difference_by_marine_region.png", dpi=300)
plt.show()

"""
Summarizes decadal totals and percent differences of a load variable (e.g.
annual DOC load) for each PSIMF watershed individually, writing one row per
watershed comparing the 2020s, 2030s, and 2040s.
"""

import pandas as pd
import os

folder_path = r"path\to\PSIMF Management\Proof_of_Concept_QC\Full_Results\Loads"

out_folder = r'path\to\PSIMF Management\Proof_of_Concept_QC\Decadal_Analysis_By_Watershed'

variable_of_interest = 'DOC_Loss(kg/d)'
variable_name = 'Annual DOC Load'

results_df = pd.DataFrame(columns=["Watershed", 2020, 2030, 2040, "Percent Diff 2030 to 2020", "Percent Diff 2040 to 2020"])

for root, dirs, files in os.walk(folder_path):
    for file in files:
        if 'SSM_Loads' in file:
            watershed_name = file.split('_')[0]
            watershed_df = pd.read_csv(os.path.join(folder_path, file), usecols=[variable_of_interest, 'Date'], parse_dates=['Date'])
    
            # Add the year to the data and filter to past 2010
            watershed_df["Year"] = watershed_df["Date"].dt.year
            watershed_df = watershed_df[watershed_df["Year"] >= 2010]
    
            # Filter additional years as desired
            year_range = list(range(2020, 2050))
            watershed_df = watershed_df[watershed_df["Year"].isin(year_range)]
    
            # Add the decade to the data
            watershed_df["Decade"] = (watershed_df["Year"] // 10) * 10

            # Sum total load within each year
            year_totals = (
                watershed_df.groupby(["Year", "Decade"])[variable_of_interest]
                .sum()
                .reset_index()
            )

            # Average those yearly totals across each decade
            decade_summary = (
                year_totals.groupby(["Decade"])[variable_of_interest]
                .mean()
            )
    
            val_2020 = decade_summary.get(2020, pd.NA)
            val_2030 = decade_summary.get(2030, pd.NA)
            val_2040 = decade_summary.get(2040, pd.NA)
            pct_diff_2030 = ((val_2030 - val_2020) / val_2020) * 100
            pct_diff_2040 = ((val_2040 - val_2020) / val_2020) * 100
    
            new_row = pd.DataFrame([{
                "Watershed": watershed_name,
                2020: val_2020,
                2030: val_2030,
                2040: val_2040,
                "Percent Diff 2030 to 2020": pct_diff_2030,
                "Percent Diff 2040 to 2020": pct_diff_2040
            }])

            results_df = pd.concat([results_df, new_row], ignore_index=True)

# After all the results have been compiled, save the dataframe
results_df.to_csv(f'{out_folder}/{variable_name}_decadal_by_watershed.csv', index=False)

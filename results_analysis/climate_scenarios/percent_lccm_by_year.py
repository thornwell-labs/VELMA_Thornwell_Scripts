"""
Converts LCCM land cover area outputs into per-watershed yearly proportions of
developed, forested, and agricultural cover (2011-2100), writing one
land_cover_proportions CSV per watershed for correlation with hydrologic
change.
"""

import pandas as pd

lccm_data_folder = "path/to/PSIMF Management/LCCM_QC"
lccm_data_path = f"{lccm_data_folder}/calculated_areas_velma_2011_to_2100.csv"

full_df = pd.read_csv(lccm_data_path)
developed_classes = ["Open Space", "Low Intensity", "Medium Intensity", "Developed"]

# Obtain lists of unique watersheds and years
watersheds = full_df["Feature_Name"].unique()
years = full_df["Year"].unique()

for watershed in watersheds:
    df_out = pd.DataFrame(index=years)
    df_out.index.name = "Year"
    subset = full_df[full_df["Feature_Name"] == watershed]
    for year in years:
        yearly_data = subset[subset["Year"] == year]
        df_out.loc[year, "Percent_Developed"] = yearly_data[yearly_data["Landcover_Class"].isin(developed_classes)]["Proportion"].sum()
        df_out.loc[year, "Percent_Forested"] = yearly_data[yearly_data["Landcover_Class"] == "Forest"]["Proportion"].sum()
        df_out.loc[year, "Percent_Agriculture"] = yearly_data[yearly_data["Landcover_Class"] == "Agriculture"]["Proportion"].sum()
    df_out.to_csv(f"{lccm_data_folder}/{watershed}_land_cover_proportions.csv")
    
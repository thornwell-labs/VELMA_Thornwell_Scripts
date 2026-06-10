"""
Analyzes seasonal hydrologic patterns across the PSIMF watersheds from the full
hydro results files. Assigns each day to a season, aggregates per-watershed
seasonal statistics, and averages across watersheds to summarize regional
seasonal behavior.
"""

import os
import pandas as pd

folder_path = r'path\to\PSIMF Management\Proof_of_Concept_QC\Full_Results'
file_paths = []
for file in os.listdir(folder_path):
    if 'full_hydro' in file:
        valid_path = os.path.join(folder_path, file)
        file_paths.append(valid_path)

season_dict = {
    'Spring': range(91, 150),   # Apr–Jun
    'Summer': range(150, 258),  # Jul–Sep
    'Fall': range(258, 367),    # Oct–Dec
    'Winter': list(range(1, 91))  # Jan–Mar
}

def jday_to_season(jday: int) -> str:
    for season, days in season_dict.items():
        if jday in days:
            return season
    return 'Unknown'


# Collect per-watershed results into a list, then average across watersheds
all_results = []

for file_path in file_paths:
    df = pd.read_csv(file_path)
    df['Season'] = df['Day'].apply(jday_to_season)
    df = df[df['Year'] >= 2020]
    df = df[df['Year'] < 2050]

    # Annual sums for fluxes
    annual_flux = df.groupby('Year')[['Rain(mm_day)_Delineated_Average', 'Snow_Melt(mm_day)_Delineated_Average', 'ET(mm_day)_Delineated_Average']].sum()

    # Seasonal sums for fluxes
    seasonal_flux = df.groupby(['Year', 'Season'])[['Rain(mm_day)_Delineated_Average', 'Snow_Melt(mm_day)_Delineated_Average', 'ET(mm_day)_Delineated_Average']].sum()

    # Annual means for state variables
    annual_state = df.groupby('Year')[['Air_Temperature(degC)_Delineated_Average', 'Soil_Saturation_Fraction_Delineated_Average_Layer_1']].mean()

    # Seasonal means for state variables
    seasonal_state = df.groupby(['Year', 'Season'])[['Air_Temperature(degC)_Delineated_Average', 'Soil_Saturation_Fraction_Delineated_Average_Layer_1']].mean()

    # Flatten to one row per Year with columns for annual + each season
    rows = []

    for year in sorted(df['Year'].unique()):
        row = {'Year': year}

        # Annual fluxes
        if year in annual_flux.index:
            row['Rain(mm_day)_annual'] = annual_flux.loc[year, 'Rain(mm_day)_Delineated_Average']
            row['Snow_Melt(mm_day)_annual'] = annual_flux.loc[year, 'Snow_Melt(mm_day)_Delineated_Average']
            row['ET_annual'] = annual_flux.loc[year, 'ET(mm_day)_Delineated_Average']

        # Annual state means
        if year in annual_state.index:
            row['Tair_annual'] = annual_state.loc[year, 'Air_Temperature(degC)_Delineated_Average']
            row['soil_sat_annual'] = annual_state.loc[year, 'Soil_Saturation_Fraction_Delineated_Average_Layer_1']

        # Per-season values
        for season in ['Winter', 'Spring', 'Summer', 'Fall']:
            if (year, season) in seasonal_flux.index:
                row[f'Rain(mm_day)_{season}'] = seasonal_flux.loc[(year, season), 'Rain(mm_day)_Delineated_Average']
                row[f'Snow_Melt(mm_day)_{season}'] = seasonal_flux.loc[(year, season), 'Snow_Melt(mm_day)_Delineated_Average']
                row[f'ET_{season}'] = seasonal_flux.loc[(year, season), 'ET(mm_day)_Delineated_Average']

            if (year, season) in seasonal_state.index:
                row[f'Tair_{season}'] = seasonal_state.loc[(year, season), 'Air_Temperature(degC)_Delineated_Average']
                row[f'soil_sat_{season}'] = seasonal_state.loc[(year, season), 'Soil_Saturation_Fraction_Delineated_Average_Layer_1']

        rows.append(row)

    result_df = pd.DataFrame(rows)
    all_results.append(result_df.set_index('Year'))

# Average each variable across watersheds
# Align on Year and then take mean across stacked dataframes
if all_results:
    combined = pd.concat(all_results, axis=1, keys=range(len(all_results)))
    # After this, combined has a multi-index on columns: (watershed_idx, variable)
    # Take mean across watershed dimension
    avg_across_watersheds = combined.groupby(level=1, axis=1).mean()
    avg_across_watersheds.reset_index(inplace=True)  # bring Year back as a column

    # Save separate .csv file for each variable group
    # Example: one CSV for fluxes, one for state variables
    flux_cols = [c for c in avg_across_watersheds.columns if any(x in c for x in ['Rain', 'Snow_Melt', 'ET'])]
    state_cols = [c for c in avg_across_watersheds.columns if any(x in c for x in ['Tair', 'soil_sat'])]

    flux_out = avg_across_watersheds[['Year'] + flux_cols]
    state_out = avg_across_watersheds[['Year'] + state_cols]

    out_folder = os.path.join(folder_path, 'aggregated_outputs')
    os.makedirs(out_folder, exist_ok=True)

    flux_out.to_csv(os.path.join(out_folder, 'fluxes_seasonal_annual_mean_across_watersheds.csv'), index=False)
    state_out.to_csv(os.path.join(out_folder, 'states_seasonal_annual_mean_across_watersheds.csv'), index=False)
    
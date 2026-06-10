"""
Compiles hydrologic variables from a series of decadal PSIMF VELMA runs into
one continuous dataset. Concatenates DailyResults files (1987-2099), collects
runoff, snow, ET, soil moisture, and related columns, and computes seasonal
totals for trend analysis.
"""

import pandas as pd
import os

watershed = 'Samish'
results_parent_folder = 'path/to/VELMA_Watersheds/Samish/Results/'

# Collect seasonal totals (mm) in runoff, rainfall, snowmelt, and ET
daily_results_paths = ["path/to/VELMA_Watersheds/Samish/Results/Samish_PSIMF_1987_2019/Samish__1987_2019_DailyResults.csv",
                       "path/to/VELMA_Watersheds/Samish/Results/Samish_PSIMF_2020_2029/Samish_2020_2029_DailyResults.csv",
                       "path/to/VELMA_Watersheds/Samish/Results/Samish_PSIMF_2030_2039/Samish_2030_2039_DailyResults.csv",
                       "path/to/VELMA_Watersheds/Samish/Results/Samish_PSIMF_2040_2049/Samish_2040_2049_DailyResults.csv",
                       "path/to/VELMA_Watersheds/Samish/Results/Samish_PSIMF_2050_2059/Samish_PSIMF_2050_2059_DailyResults.csv",
                       "path/to/VELMA_Watersheds/Samish/Results/Samish_PSIMF_2060_2069/Samish_PSIMF_2060_2069_DailyResults.csv",
                       "path/to/VELMA_Watersheds/Samish/Results/Samish_PSIMF_2070_2079/Samish_PSIMF_2070_2079_DailyResults.csv",
                       "path/to/VELMA_Watersheds/Samish/Results/Samish_PSIMF_2080_2089/Samish_PSIMF_2080_2089_DailyResults.csv",
                       "path/to/VELMA_Watersheds/Samish/Results/Samish_PSIMF_2090_2099/Samish_PSIMF_2090_2099_DailyResults.csv"]

daily_result_columns = ['Year', 'Day', 'Runoff_All(mm/day)_Delineated_Average', 'Snow_Melt(mm/day)_Delineated_Average', 'Snow_Depth(mm)_Delineated_Average',
                        'Snow(mm/day)_Delineated_Average','Rain(mm/day)_Delineated_Average', 'ET(mm/day)_Delineated_Average', 'Standing_Water(mm)_Delineated_Average',
                        'Soil_Saturation_Fraction_(Definition:_mm_water_stored_in_layer_/_(layer_porosity_fraction_*_mm_layer_thickness))_Delineated_Average_Layer_1',
                        'Water_Stored(mm)_Delineated_Average_Layer_1', 'Water_Stored(mm)_Delineated_Average_Layer_2', 'Water_Stored(mm)_Delineated_Average_Layer_3',
                        'Water_Stored(mm)_Delineated_Average_Layer_4', 'Air_Temperature(degC)_Delineated_Average', 'Groundwater_Storage_Added(mm/day)_Delineated_Average', 
                        'Biomass_Leaf(gC/m2)_Delineated_Average']

# Combine all the dataframes into one
daily_frames = []
for path in daily_results_paths:
    df = pd.read_csv(path, usecols=daily_result_columns)
    daily_frames.append(df)
daily_combined = pd.concat(daily_frames)

# Remove definition from soil saturation fraction column
daily_combined.rename(
    columns={'Soil_Saturation_Fraction_(Definition:_mm_water_stored_in_layer_/_(layer_porosity_fraction_*_mm_layer_thickness))_Delineated_Average_Layer_1': 
        'Soil_Saturation_Fraction_Delineated_Average_Layer_1'}, inplace=True)

# Remove any slashes from the column names
daily_combined.columns = daily_combined.columns.str.replace('/', '_', regex=False)

# Write the full results file
daily_combined.to_csv(os.path.join(results_parent_folder, f'{watershed}_PSIMF_full_hydro_results.csv'), index=False)

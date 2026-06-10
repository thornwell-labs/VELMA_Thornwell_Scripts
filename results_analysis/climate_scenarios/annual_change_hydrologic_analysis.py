"""
Examines how much of the yearly change in runoff across the PSIMF decadal runs
(1987-2099) is explained by changes in rainfall, snowmelt, soil saturation,
and evapotranspiration, compiling all decades into one yearly-change table.
"""

import pandas as pd
import matplotlib.pyplot as plt

# How much of the change in runoff is explainable by changes in rainfall, snowmelt, storage, and ET?

watershed = 'Stillaguamish'
out_path = 'path/to/VELMA_Watersheds/Stillaguamish/Analysis'

# Collect yearly change (mm) in runoff, rainfall, snowmelt, and ET
daily_results_paths = ['path/to/VELMA_Watersheds/Stillaguamish/Results/MULTI_WA_Stillaguamish30m_PSIMF_17July2025_resampled_3_Hyak/Results_244276/DailyResults.csv',
                       "path/to/VELMA_Watersheds/Stillaguamish/Results/MULTI_WA_Stillaguamish30m_PSIMF_2029_resampled_3/Results_244276/DailyResults.csv",
                       "path/to/VELMA_Watersheds/Stillaguamish/Results/MULTI_WA_Stillaguamish30m_PSIMF_2039_resampled_3/Results_244276/DailyResults.csv",
                       "path/to/VELMA_Watersheds/Stillaguamish/Results/MULTI_WA_Stillaguamish30m_PSIMF_2049_resampled_3/Results_244276/DailyResults.csv",
                       "path/to/VELMA_Watersheds/Stillaguamish/Results/MULTI_WA_Stillaguamish30m_PSIMF_2059_resampled_3/Results_244276/DailyResults.csv",
                       "path/to/VELMA_Watersheds/Stillaguamish/Results/MULTI_WA_Stillaguamish30m_PSIMF_2069_resampled_3/Results_244276/DailyResults.csv",
                       "path/to/VELMA_Watersheds/Stillaguamish/Results/MULTI_WA_Stillaguamish30m_PSIMF_2079_resampled_3/Results_244276/DailyResults.csv",
                       "path/to/VELMA_Watersheds/Stillaguamish/Results/MULTI_WA_Stillaguamish30m_PSIMF_2089_resampled_3/Results_244276/DailyResults.csv",
                       "path/to/VELMA_Watersheds/Stillaguamish/Results/MULTI_WA_Stillaguamish30m_PSIMF_2099_resampled_3/Results_244276/DailyResults.csv"]

daily_result_columns = ['Year', 'Day', 'Runoff_All(mm/day)_Delineated_Average', 'Snow_Melt(mm/day)_Delineated_Average', 
                        'Rain(mm/day)_Delineated_Average', 'ET(mm/day)_Delineated_Average',
                        'Soil_Saturation_Fraction_(Definition:_mm_water_stored_in_layer_/_(layer_porosity_fraction_*_mm_layer_thickness))_Delineated_Average_Layer_1']

# Combine all the dataframes into one before calculating percent change
daily_frames = []
for path in daily_results_paths:
    df = pd.read_csv(path, usecols=daily_result_columns)
    daily_frames.append(df)
daily_combined = pd.concat(daily_frames)

annual_totals = daily_combined.groupby('Year').agg({
    'Runoff_All(mm/day)_Delineated_Average': 'sum',
    'Snow_Melt(mm/day)_Delineated_Average': 'sum',
    'Rain(mm/day)_Delineated_Average': 'sum',
    'ET(mm/day)_Delineated_Average': 'sum',
    'Soil_Saturation_Fraction_(Definition:_mm_water_stored_in_layer_/_(layer_porosity_fraction_*_mm_layer_thickness))_Delineated_Average_Layer_1': 'sum'
})

# Baseline averages
baseline_runoff = annual_totals['Runoff_All(mm/day)_Delineated_Average'].loc[2010:2019].mean()
baseline_snowmelt = annual_totals['Snow_Melt(mm/day)_Delineated_Average'].loc[2010:2019].mean()
baseline_rainfall = annual_totals['Rain(mm/day)_Delineated_Average'].loc[2010:2019].mean()
baseline_et = annual_totals['ET(mm/day)_Delineated_Average'].loc[2010:2019].mean()
baseline_saturation = annual_totals['Soil_Saturation_Fraction_(Definition:_mm_water_stored_in_layer_/_(layer_porosity_fraction_*_mm_layer_thickness))_Delineated_Average_Layer_1'].loc[2010:2019].mean()

# Calculate change from baseline
runoff_change = annual_totals['Runoff_All(mm/day)_Delineated_Average'].loc[2010:] - baseline_runoff
snowmelt_change = annual_totals['Snow_Melt(mm/day)_Delineated_Average'].loc[2010:] - baseline_snowmelt
rainfall_change = annual_totals['Rain(mm/day)_Delineated_Average'].loc[2010:] - baseline_rainfall
et_change = annual_totals['ET(mm/day)_Delineated_Average'].loc[2010:] - baseline_et
saturation_change = annual_totals['Soil_Saturation_Fraction_(Definition:_mm_water_stored_in_layer_/_(layer_porosity_fraction_*_mm_layer_thickness))_Delineated_Average_Layer_1'].loc[2010:] - baseline_saturation

change_df = pd.DataFrame({
    'Runoff_Change_mm': runoff_change,
    'Snowmelt_Change_mm': snowmelt_change,
    'Rainfall_Change_mm': rainfall_change,
    'ET_Change_mm': et_change,
    'Layer1_Saturation_change_pct': saturation_change
})

output_path = f'{out_path}/PSIMF_Hydrologic_Change_{watershed}.csv'
change_df.to_csv(output_path, float_format='%.4f')


# Plotting the changes
plt.figure(figsize=(12, 6))

plt.plot(change_df.index, change_df['Runoff_Change_mm'], label='Runoff Change (mm)')
plt.plot(change_df.index, change_df['Snowmelt_Change_mm'], label='Snowmelt Change (mm)')
plt.plot(change_df.index, change_df['Rainfall_Change_mm'], label='Rainfall Change (mm)')
plt.plot(change_df.index, change_df['ET_Change_mm'], label='ET Change (mm)')
# plt.plot(change_df.index, change_df['Layer1_Storage_Change_mm'], label='Layer 1 Storage Change (mm)')

plt.axhline(0, color='gray', linewidth=0.8, linestyle='--', label='Baseline')

plt.title(f"Hydrologic Changes Relative to 2010–2019 Baseline ({watershed})")
plt.xlabel('Year')
plt.ylabel('Change (relative to baseline)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig(f'{out_path}/{watershed}_hydro_relative_change.png')
plt.show()
plt.close()

"""
Plots historical monthly nitrogen loads (NH4, NO3, DON) for a list of
point-source facilities to inform future-load forecasting. Flags facilities
with no 2020 data as likely no longer operational.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

# Define facility names
facility_names = ['Skookum Creek Hatchery', 'Everson STP', 'Lynden STP', 'Kendall Creek Hatchery', 'Darigold Lynden Plant', 'Ferndale STP']

# ----------------------------------------------------------------------------------------------- #

# Load facility file
point_source_folder = 'path/to/VELMA_Tools/Point_Source_Data'
facility_csv = os.path.join(point_source_folder, 'fac_attributes (1).csv')

# Read facility ID mapping
facility_df = pd.read_csv(facility_csv, usecols=['FAC_ID', 'FAC_NAME'], dtype='str')

fac_id_list = []
for name in facility_names:
    match = facility_df[facility_df['FAC_NAME'].str.lower() == name.lower()]
    if not match.empty:
        fac_id = match.iloc[0]['FAC_ID']
        fac_id_list.append(fac_id)
    else:
        print(f'WARNING: {name} not found in facility attributes spreadsheet')

for fac_id in fac_id_list:
    monthly_load_path = os.path.join(point_source_folder, f'{fac_id}_monthly_load.csv')
    monthly_load_df = pd.read_csv(monthly_load_path)

    # Check if 2020 data is missing
    if 2020 not in monthly_load_df['YEAR'].unique():
        print(f'2020 data is missing. Assume {fac_id} is no longer operational.')
        continue
    
    # Plot NH4, NO3, DON over time
    plt.figure(figsize=(12, 6))
    monthly_load_df['Date'] = pd.to_datetime({
    'year': monthly_load_df['YEAR'],
    'month': monthly_load_df['MONTH'],
    'day': 1
    })
    for compound in ['NH4_LOAD_KG_DAY', 'NO3_LOAD_KG_DAY', 'DON_LOAD_KG_DAY']:
        plt.plot(monthly_load_df['Date'], monthly_load_df[compound], label=compound)
    plt.title(f'N Load Over Time for Facility {fac_id}')
    plt.xlabel('Date')
    plt.ylabel('Daily Load (kg/d)')
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    # Check if 2099 data has already been forecasted
    if 2099 in monthly_load_df['YEAR'].unique():
        print(f'2099 data already forecasted for facility {fac_id}.')
        continue

    # Filter data for 2010-2020
    filtered_df = monthly_load_df[(monthly_load_df['YEAR'] >= 2010) & (monthly_load_df['YEAR'] <= 2020)]

    # Compute monthly averages
    avg_monthly = filtered_df.groupby('MONTH')[['NH4_LOAD_KG_DAY', 'NO3_LOAD_KG_DAY', 'DON_LOAD_KG_DAY']].mean()
    
    # Check for outliers in original data and missing months
    for compound in ['NH4_LOAD_KG_DAY', 'NO3_LOAD_KG_DAY', 'DON_LOAD_KG_DAY']:
        print(f"\nChecking for anomalies in {compound} for {fac_id}...")
        for month in range(1, 13):
            month_data = filtered_df[filtered_df['MONTH'] == month][compound]
            if month in avg_monthly.index and compound in avg_monthly.columns:
                month_mean = avg_monthly.loc[month, compound]
            else:
                print(f"Missing data for month {month}, compound {compound} at facility {fac_id}.")
                continue
            for val in month_data:
                if val > 10 * month_mean or val < 0.1 * month_mean:
                    print(f'{compound} for month {month}: value {val:.2f} is an outlier (avg={month_mean:.2f})')
    
    # Project monthly values into the future to 2099
    projections = []
    for year in range(2021, 2100):
        for month in range(1, 13):
            projected = {
                'YEAR': year,
                'MONTH': month,
                'NH4_LOAD_KG_DAY': avg_monthly.loc[month, 'NH4_LOAD_KG_DAY'],
                'NO3_LOAD_KG_DAY': avg_monthly.loc[month, 'NO3_LOAD_KG_DAY'],
                'DON_LOAD_KG_DAY': avg_monthly.loc[month, 'DON_LOAD_KG_DAY']
            }
            projections.append(projected)

    projections_df = pd.DataFrame(projections)

    # Round projections to the hundredths
    for col in ['NH4_LOAD_KG_DAY', 'NO3_LOAD_KG_DAY', 'DON_LOAD_KG_DAY']:
        projections_df[col] = projections_df[col].round(2)
    
    # Reorder and match original columns
    projections_df = projections_df[['YEAR', 'MONTH', 'NH4_LOAD_KG_DAY', 'NO3_LOAD_KG_DAY', 'DON_LOAD_KG_DAY']]

    # Append to original DataFrame
    combined_df = pd.concat([monthly_load_df[['YEAR', 'MONTH', 'NH4_LOAD_KG_DAY', 'NO3_LOAD_KG_DAY', 'DON_LOAD_KG_DAY']], projections_df], ignore_index=True)

    # Save combined data back to the original file (overwrite)
    monthly_load_path = os.path.join(point_source_folder, f'{fac_id}_monthly_load.csv')
    combined_df.to_csv(monthly_load_path, index=False)
    print(f'Forecasted data appended to {monthly_load_path}')

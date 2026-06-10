"""
Checks the point-source nutrient loads dataset for gaps. Reports, per
facility, any months missing entirely from 2005-2020 and any months where the
total nitrogen load value is blank.
"""

import pandas as pd

# Load data
file_path = 'path/to/nutrient_loads.csv'
df = pd.read_csv(file_path)  # Adjust delimiter if needed

# Drop missing years/months and ensure they're type int
df.dropna(subset=['YEAR', 'MONTH'], inplace=True)
df['YEAR'] = pd.to_numeric(df['YEAR']).astype(int)
df['MONTH'] = pd.to_numeric(df['MONTH']).astype(int)

# Create a Date column to use index
df['Date'] = pd.to_datetime(df['YEAR'].astype(str) + '-' + df['MONTH'].astype(str), format='%Y-%m')

# Define the expected date range
expected_dates = pd.date_range(start='2005-01-01', end='2020-12-01', freq='MS')

# Dictionary to store missing dates per facility
missing_data = {}

for fac_id, group in df.groupby('FAC_ID'):
    group = group.set_index('Date').sort_index()  # Ensure chronological order
    
    # Find missing dates
    missing_dates = set(expected_dates) - set(group.index)
    
    # Check if TN_LOAD_KG_MO is missing for any existing dates
    tn_missing_dates = group[group['TN_LOAD_KG_MO'].isna()].index.tolist()
    
    if missing_dates or tn_missing_dates:
        missing_data[fac_id] = {
            "Missing Dates": sorted(missing_dates),
            "TN Missing": sorted(tn_missing_dates)
        }

# Print results
for fac_id, issues in missing_data.items():
    print(f"Facility {fac_id} has missing data:")
    if issues["Missing Dates"]:
        print("  Missing months:", [d.strftime('%Y-%m') for d in issues["Missing Dates"]])
    if issues["TN Missing"]:
        print("  TN_LOAD_KG_MO missing for:", [d.strftime('%Y-%m') for d in issues["TN Missing"]])
    print("-" * 50)
print(f'All facilities missing data: {list(missing_data.keys())}')
print(f'Number of facilities missing data: {len(list(missing_data.keys()))}')

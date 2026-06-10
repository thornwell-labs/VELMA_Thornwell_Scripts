"""
Creates bar charts of average monthly total nitrogen loads by point-source
facility type for each watershed, and ranks facilities into TN magnitude
classes for map symbology. Uses the table from monthly_tn_calculator.py.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

csv_path = 'path/to/VELMA_Tools/Point_Source_Data/PSIMF_fac_monthly_tn.csv'
out_csv_path = 'path/to/VELMA_Tools/Point_Source_Data/PSIMF_fac_ranked.csv'

df = pd.read_csv(csv_path)

# Add ranking for average monthly TN for map visualization purposes
df['TN_Rank'] = np.nan
for i, row in df.iterrows():
    if row['AVG_TN_LOAD_KG_MO'] < 10:
        df.loc[i, 'TN_Rank'] = 0
    elif row['AVG_TN_LOAD_KG_MO'] < 100:
        df.loc[i, 'TN_Rank'] = 1
    elif row['AVG_TN_LOAD_KG_MO'] < 1000:
        df.loc[i, 'TN_Rank'] = 2
    else:
        df.loc[i, 'TN_Rank'] = 3
df.to_csv(out_csv_path, index=False)

# Initialize dictionary to store values for the bar chart
watershed_dict = {}
    
for i, row in df.iterrows():
    watershed = row['Watershed']
    fac_type = row['FAC_TYPE']
    tn = row['AVG_TN_LOAD_KG_MO']

    if watershed not in watershed_dict:
        watershed_dict[watershed] = {}

    if fac_type not in watershed_dict[watershed]:
        watershed_dict[watershed][fac_type] = 0

    watershed_dict[watershed][fac_type] += tn

# Convert facility types to descriptive names
fac_type_map = {
    'sic_0921': 'Hatcheries',
    'sic_INDU': 'Industrial',
    'sic_4952': 'WWTP'
}

# Convert the nested dictionary into a DataFrame for plotting
plot_df = pd.DataFrame(watershed_dict).fillna(0).T  # Transpose so watersheds are rows
plot_df.rename(columns=fac_type_map, inplace=True)

# Plot the stacked bar chart
plot_df.plot(kind='bar', stacked=True, figsize=(12, 7))
plt.ylabel('Average Monthly TN Load (kg)')
plt.xlabel('Watershed')
plt.title('Average Monthly TN Load by Watershed and Facility Type')
plt.legend(title='Facility Type', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

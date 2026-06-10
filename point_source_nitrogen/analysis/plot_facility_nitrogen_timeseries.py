"""
Plots a single column (e.g. monthly total nitrogen load) of the point-source
nutrient loads dataset over time for one facility. Quick-look QC tool.
"""

import pandas as pd
import matplotlib.pyplot as plt

# Set file path and desired facility ID
file_path = 'path/to/nutrient_loads.csv'
fac_id = 'WAG131024'
desired_column = 'TN_LOAD_KG_MO'

df = pd.read_csv(file_path)

# Drop missing years/months and ensure they're type int
df.dropna(subset=['YEAR', 'MONTH'], inplace=True)
df['YEAR'] = pd.to_numeric(df['YEAR']).astype(int)
df['MONTH'] = pd.to_numeric(df['MONTH']).astype(int)
df['FAC_ID'] = df['FAC_ID'].astype(str)

# Create a Date column to use index
df['Date'] = pd.to_datetime(df['YEAR'].astype(str) + '-' + df['MONTH'].astype(str), format='%Y-%m')

filtered_df = df[df['FAC_ID'] == fac_id]
plt.plot(filtered_df['Date'], filtered_df[desired_column])
plt.title(f'{desired_column} for {fac_id} Over Time')
plt.xlabel('Date')
plt.ylabel(desired_column)
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
plt.tight_layout()  # To avoid clipping of labels
plt.show()

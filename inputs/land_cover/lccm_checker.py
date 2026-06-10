"""
QC check for Land Cover Change Model (LCCM) disturbance driver files. Counts
how many cells change land cover each year in the LCCM CSV and plots the
percent of the watershed map changed per year.
"""

import pandas as pd
import matplotlib.pyplot as plt

# Define these
cell_count = 4989*5373
name = 'Skagit'
file_path = 'path/to/VELMA_Watersheds/Skagit/Data_Inputs30m/o_6_LCCM/SkagitStatusQuo_modifyLandcoverDriverData_HistoricDisturbace.csv'


# ----------------------- Don't edit anything below here ------------------------
# Load the CSV file 
df = pd.read_csv(file_path, header=None)  
df.columns = ['Index', 'Year', 'Jday']  # Assign columns because the original csv doesn't have them labeled

years = range(2001, 2100) # list of years 2001 through 2099
# Count the number of rows in the df that have a record matching each year in the list
row_counts = []
for year in years:
    row_count = len(df[df['Year'] == year])
    row_counts.append(row_count)

percents = [round(count / cell_count, 5) * 100 for count in row_counts]

# Plot percent of map changed by year
plt.figure()
plt.plot(years, percents)
plt.xlabel('Year')
plt.ylabel('Percent of cells changed')
plt.title(f'{name} land cover changes by year')
plt.savefig(f'path/to/PSIMF Management/LCCM_QC/{name}_LCCM_plot.png')
plt.show()

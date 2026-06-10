"""
Plots how a single VELMA parameter changed across model versions as a bar
chart, with the original value marked by a reference line. Non-cover-specific
counterpart to cover_parameter_comparison_plots.py.
"""

import pandas as pd
import matplotlib.pyplot as plt

# Define the file path
file_path = 'path/to/VELMA_Watersheds/Analysis/Nutrient_model_parameter_changes.xlsx'

# Load the Excel file and get sheet names
parameter_changes_file = pd.ExcelFile(file_path)
model_names = parameter_changes_file.sheet_names
parameter_of_interest = 'soil/Medium_CN24/docLossFraction'

# Store values and corresponding model names
parameter_list = []

for model_name in model_names:
    df = pd.read_excel(parameter_changes_file, sheet_name=model_name)
    
    # Get the new value for the parameter
    new_value = df.loc[df['Parameter'] == parameter_of_interest, 'New Value'].values[0]
    parameter_list.append(new_value)

# Get old value (assuming it's the same across sheets)
old_value = df.loc[df['Parameter'] == parameter_of_interest, 'Old Value'].values[0]

# --- Plotting ---
plt.figure(figsize=(10, 6))
bars = plt.bar(model_names, parameter_list, color='skyblue', edgecolor='black')

# Add a horizontal line for the old value
plt.axhline(y=old_value, color='red', linestyle='--', label=f'Old Value = {old_value:.6f}')

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height, f'{height:.6f}', ha='center', va='bottom', fontsize=9)

plt.title(f'New Values of "{parameter_of_interest.split("/")[-1]}"')
plt.ylabel('New Parameter Value')
plt.xticks(rotation=45, ha='right')
plt.legend()
plt.tight_layout()
plt.show()

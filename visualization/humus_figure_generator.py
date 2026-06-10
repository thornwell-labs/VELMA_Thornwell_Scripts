"""
Plots total and per-layer humus carbon pools over time across decadal PSIMF
runs for a watershed, overlaying each decade's results to check humus pool
stability through the simulation period.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

# Define these
name = "Dungeness"
results_folders = {
    "1987–2019": "path/to/VELMA_Watersheds/Dungeness/Dungeness_Working/Results/MULTI_WA_Dungeness30m_PSIMF_14Jul2025/Results_618422",
    "2020–2029": "path/to/VELMA_Watersheds/Dungeness/Dungeness_Working/Results/MULTI_WA_Dungeness30m_PSIMF_2029/Results_618422",
    "2030–2039": "path/to/VELMA_Watersheds/Dungeness/Dungeness_Working/Results/MULTI_WA_Dungeness30m_PSIMF_2039/Results_618422",
    # add more decades as they process
}

# ---------------------- Code will run without editing anything below this line ------------------

figure_outdir = f"path/to/PSIMF Management/Proof_of_Concept_QC/Figures/{name}"
os.makedirs(figure_outdir, exist_ok=True)

data_columns = [
    'Humus_Pool(gC/m2)_Delineated_Average',
    'Humus(gC/m2)_Delineated_Average_Layer_1',
    'Humus(gC/m2)_Delineated_Average_Layer_2',
    'Humus(gC/m2)_Delineated_Average_Layer_3',
    'Humus(gC/m2)_Delineated_Average_Layer_4'
]

dfs = {}

# Load all available results
for label, folder in results_folders.items():
    csv_path = os.path.join(folder, "DailyResults.csv")
    if not os.path.exists(csv_path):
        print(f"Skipping {label}, missing {csv_path}")
        continue

    df = pd.read_csv(csv_path, usecols=['Year', 'Day'] + data_columns)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + df['Day'].astype(str), format='%Y%j')
    df = df.set_index('Date')

    # Compute total humus across layers
    df['Total Humus'] = df[data_columns].sum(axis=1)
    dfs[label] = df

# Plot all scenarios together
plt.figure(figsize=(12, 7))
for label, df in dfs.items():
    plt.plot(df.index, df['Total Humus'], label=label)

plt.xlabel('Date')
plt.ylabel('Average Delineated Humus (gC/m2)')
plt.title(f'Humus Stability in {name} Outlet Catchment')
plt.legend()
plt.grid(True)

plt.savefig(os.path.join(figure_outdir, "Humus_Stability.png"))
plt.show()

"""
Computes annual percent change in carbon and nitrogen pools (biomass, litter,
humus, NH4, NO3, DON, DOC) across multiple watersheds' end-state VELMA runs,
compiling one table per pool variable for the chemistry pool stability
analysis. Companion to summarize_annual_pct_change.py.
"""

import pandas as pd
import os

result_folders = {
    'Juanita': "path/to/VELMA_Watersheds/Juanita/Results/MULTI_WA_Juanita30m_GetEndState_Hyak/Results_27645/DailyResults.csv",
    'Big Beef': "path/to/VELMA_Watersheds/Big_Beef/Results/MULTI_WA_BigBeef30m_GetEndState_Hyak/Results_23023/DailyResults.csv",
    'Huge': "path/to/VELMA_Watersheds/Huge/Results/MULTI_WA_Huge30m_GetEndState/Results_75524/DailyResults.csv",
    'Mercer': "path/to/VELMA_Watersheds/Mercer/Results/MULTI_WA_Mercer30m_GetEndState/Results_61512/DailyResults.csv",
    'Issaquah': "path/to/VELMA_Watersheds/Issaquah/Results/MULTI_WA_Issaquah30m_GetEndState/Results_60953/DailyResults.csv",
    'Goldsborough': "path/to/VELMA_Watersheds/Goldsborough/Results/MULTI_WA_Goldsborough30m_GetEndState/Results_238500/DailyResults.csv",
    'Quilcene': "path/to/VELMA_Watersheds/Quilcene/Results/MULTI_WA_Quilcene30m_GetEndState/Results_243053/DailyResults.csv",
    'Hoko': "path/to/VELMA_Watersheds/Hoko/Results/MULTI_WA_Hoko30m_GetEndState/Results_100002/DailyResults.csv",
    'Duckabush': "path/to/VELMA_Watersheds/Duckabush/Results/MULTI_WA_Duckabush30m_GetEndState/Results_150181/DailyResults.csv"
}

out_path = 'path/to/Manuscripts/Chemistry Pool Analysis'

col_list = [
    'agBiomass_Pool(gC/m2)_Delineated_Average',
    'bgBiomass_Pool(gC/m2)_Delineated_Average',
    'agLitter_Pool(gC/m2)_Delineated_Average',
    'bgLitter_Pool(gC/m2)_Delineated_Average',
    'Humus_Pool(gC/m2)_Delineated_Average',
    'NH4_Pool(gN/m2)_Delineated_Average',
    'NO3_Pool(gN/m2)_Delineated_Average',
    'DON_Pool(gN/m2)_Delineated_Average',
    'DOC_Pool(gC/m2)_Delineated_Average',
    'NH4_Loss(gN/day/m2)_Delineated_Average',
    'NO3_Loss(gN/day/m2)_Delineated_Average',
    'DON_Loss(gN/day/m2)_Delineated_Average',
    'DOC_Loss(gC/day/m2)_Delineated_Average'
]

param_dfs = {param: pd.DataFrame() for param in col_list}

for watershed, path in result_folders.items():
    df = pd.read_csv(path, usecols=['Year'] + col_list)
    yearly_avg = df.groupby('Year').mean()
    annual_change = yearly_avg.pct_change()

    for param in col_list:
        # Add this watershed's annual change series as a column to the parameter dataframe
        param_dfs[param][watershed] = annual_change[param]

# Save each parameter dataframe to CSV
for param, df in param_dfs.items():
    # Clean the parameter name for filename (remove spaces, parentheses, etc.)
    safe_param_name = param.split('(')[0]
    filename = f"{safe_param_name}_annual_change.csv"
    df.to_csv(os.path.join(out_path, filename))
    
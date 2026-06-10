"""
Computes annual statistics for the QNM (Qualitative Network Model) team from
SSM-format VELMA results: runoff totals and extremes, peak/minimum timing,
5-day rolling extremes, and water temperature metrics, one output table per
watershed.
"""

import pandas as pd
import os

results_path = 'path/to/PSIMF Management/Proof_of_Concept_QC/Full_Results'
output_path = 'path/to/PSIMF Management/QNM/Data'

for root, dirs, files in os.walk(results_path):
    for file in files:
        name = file.split('_')[0]
        df = pd.read_csv(os.path.join(root, file), parse_dates=['Date'])
        
        # Determine year, group by year, and start result dataframe
        df['Year'] = df['Date'].dt.year
        df = df[df['Year'] >= 2010]
        grouped = df.groupby('Year')
        results = pd.DataFrame(index=grouped.groups.keys())
        
        # Runoff metrics
        # Conversion to ckm: m3/s/d * (86400 s / d) * (km3 / 1e+9 m3)
        results['sum_runoff_ckm'] = grouped['Runoff(m3/s)'].sum() * 86400 / 1e9
        results['peak_daily_runoff_cms'] = grouped['Runoff(m3/s)'].max()
        results['Jday_peak_daily_runoff'] = grouped['Runoff(m3/s)'].idxmax().apply(lambda i: df.loc[i, 'Date'].dayofyear)
        results['min_daily_runoff_cms'] = grouped['Runoff(m3/s)'].min()
        results['Jday_min_daily_runoff'] = grouped['Runoff(m3/s)'].idxmin().apply(lambda i: df.loc[i, 'Date'].dayofyear)

        # 5-day rolling average
        df['Runoff_5day'] = df['Runoff(m3/s)'].rolling(5).mean()
        grouped_5day = df.groupby('Year')
        results['min_5_day_runoff_cms'] = grouped_5day['Runoff_5day'].min()

        # Temperature metrics
        results['peak_daily_temp_degC'] = grouped['Water_Surface_Temperature(degrees_C)'].max()
        results['Jday_peak_daily_temp_degC'] = grouped['Water_Surface_Temperature(degrees_C)'].idxmax().apply(lambda i: df.loc[i, 'Date'].dayofyear)
        df['Temp_5day'] = df['Water_Surface_Temperature(degrees_C)'].rolling(5).mean()
        results['peak_5_day_temp_degC'] = grouped_5day['Temp_5day'].max()

        # Nutrient metrics
        nutrient_cols = ['NH4_Loss(mg/L)', 'NO3_Loss(mg/L)', 'DON_Loss(mg/L)', 'DOC_Loss(mg/L)']
        for col in nutrient_cols:
            if col in df.columns:
                # Build name for the new column
                mass_col = col.replace('(mg/L)', '_kg').replace(' ', '_')
                conc = df[col]
                flow = df['Runoff(m3/s)']
                # mass in kg/day: mg/L * m3/s * (86400 s/d) * (1000 L/m3) * (kg/1e6 mg)
                df[mass_col] = conc * flow * 86400 * 1000 / 1e6
                results[f'sum_{mass_col}'] = grouped[mass_col].sum()

        results.reset_index(inplace=True)
        results.rename(columns={'index': 'Year'}, inplace=True)

        out_name = f'{name}_Yearly_QNM_Statistics.csv'
        out_path = os.path.join(output_path, out_name)
        results.to_csv(out_path, index=False)
        print(f"Wrote summary for {file} -> {out_path}")



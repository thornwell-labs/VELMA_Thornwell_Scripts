"""
Computes annual runoff statistics (total, mean, min, max) per watershed from
SSM-format result files, for the historical baseline and each future decade,
writing one stats CSV per watershed and period.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

root_folder = 'path/to/PSIMF Management/Proof_of_Concept_QC'
out_folder = root_folder+'/Runoff_Analysis'
historic_folder = root_folder+'/2019_Results'

for root, dirs, files in os.walk(historic_folder):
    for file in files:
        name = file.split('_')[0]
        df = pd.read_csv(root+'/'+file, usecols=['Date', 'Runoff(m3/s)'], parse_dates=['Date'])
        historic_totals = df.groupby(df['Date'].dt.year)['Runoff(m3/s)'].sum()
        historic_means = df.groupby(df['Date'].dt.year)['Runoff(m3/s)'].mean()
        historic_mins = df.groupby(df['Date'].dt.year)['Runoff(m3/s)'].min()
        historic_maxs = df.groupby(df['Date'].dt.year)['Runoff(m3/s)'].max()
        data = {'Total': historic_totals, 'Mean': historic_means, 'Min': historic_mins, 'Max': historic_maxs}
        out_df = pd.DataFrame(data)
        os.makedirs(f'{out_folder}/{name}', exist_ok=True)
        out_df.to_csv(f'{out_folder}/{name}/{name}_historic_annual_runoff_stats.csv')

decades = ['2029', '2039', '2049', '2059', '2069', '2079', '2089', '2099']
for decade in decades:
    for root, dirs, files in os.walk(f'{root_folder}/{decade}_Results'):
        for file in files:
            name = file.split('_')[0]
            df = pd.read_csv(root+'/'+file, usecols=['Date', 'Runoff(m3/s)'], parse_dates=['Date'])
            decade_totals = df.groupby(df['Date'].dt.year)['Runoff(m3/s)'].sum()
            decade_means = df.groupby(df['Date'].dt.year)['Runoff(m3/s)'].mean()
            decade_mins = df.groupby(df['Date'].dt.year)['Runoff(m3/s)'].min()
            decade_maxs = df.groupby(df['Date'].dt.year)['Runoff(m3/s)'].max()
            data = {'Total': decade_totals, 'Mean': decade_means, 'Min': decade_mins, 'Max': decade_maxs}
            out_df = pd.DataFrame(data)
            out_df.to_csv(f'{out_folder}/{name}/{name}_{decade}_annual_runoff_stats.csv')

for root, dirs, files in os.walk(out_folder):
    for watershed in dirs:
        watershed_path = os.path.join(out_folder, watershed)
        files = [f for f in os.listdir(watershed_path) if f.endswith('_annual_runoff_stats.csv')]

        # Separate historic and future files
        historic_file = [f for f in files if 'historic' in f]
        decade_files = [f for f in files if any(dec in f for dec in decades)]

        if not historic_file:
            continue  # Skip if no historic data found

        # Load historic data
        hist_df = pd.read_csv(os.path.join(watershed_path, historic_file[0]))
        hist_df = hist_df.set_index('Date')
        historic_avg_total = hist_df.loc[(hist_df.index >= 2010) & (hist_df.index <= 2019), 'Total'].mean()

        # Prepare dataframe to collect percent changes
        comparison_data = []

        # Start with historic data
        all_data = [hist_df]

        for f in decade_files:
            decade_label = [d for d in decades if d in f][0]
            dec_df = pd.read_csv(os.path.join(watershed_path, f))
            dec_df = dec_df.set_index('Date')

            # Calculate mean total runoff for that decade
            decade_avg_total = dec_df['Total'].mean()

            # Percent difference relative to historic baseline
            percent_diff = round(((decade_avg_total - historic_avg_total) / historic_avg_total) * 100, 2)
            comparison_data.append({'Decade': decade_label, 'PercentDiff': percent_diff})

            # Add to list for full time-series
            all_data.append(dec_df)

        # Save comparison summary
        comp_df = pd.DataFrame(comparison_data)
        comp_df.to_csv(os.path.join(watershed_path, f'{watershed}_decadal_percent_change.csv'), index=False)

        # Combine all time periods into one continuous time series
        combined_df = pd.concat(all_data).sort_index().reset_index()

        # Plot mean runoff as a solid line, min/max as dashed lines
        plt.figure(figsize=(10, 6))
        plt.plot(combined_df['Date'], combined_df['Mean'], color='tab:blue', linewidth=2, label='Annual Mean')
        plt.plot(combined_df['Date'], combined_df['Min'], color='tab:blue', linestyle='--', linewidth=1, label='Annual Min/Max')
        plt.plot(combined_df['Date'], combined_df['Max'], color='tab:blue', linestyle='--', linewidth=1)

        plt.title(f'Annual Runoff Summary: {watershed}')
        plt.xlabel('Year')
        plt.ylabel('Runoff (m³/s)')
        plt.legend()
        plt.tight_layout()

        plt.savefig(os.path.join(watershed_path, f'{watershed}_annual_runoff_plot.png'), dpi=300)
        plt.close()
        

# === Summarize all percent change files into one table ===
summary_data = {}

# Loop through each watershed folder again
for watershed in os.listdir(out_folder):
    watershed_path = os.path.join(out_folder, watershed)
    if not os.path.isdir(watershed_path):
        continue

    percent_file = os.path.join(watershed_path, f'{watershed}_decadal_percent_change.csv')
    if not os.path.exists(percent_file):
        continue
    
    try:
        df = pd.read_csv(percent_file)
        if df.empty or 'Decade' not in df.columns or 'PercentDiff' not in df.columns:
            print(f"Skipping {watershed}: empty or invalid percent change file.")
            continue
    except Exception as e:
        print(f"Skipping {watershed} due to read error: {e}")
        continue
    
    df.set_index('Decade', inplace=True)
    summary_data[watershed] = df['PercentDiff']

# Combine all into a single DataFrame
summary_df = pd.DataFrame(summary_data)

# Ensure decades are sorted in chronological order
summary_df = summary_df.reindex(sorted(summary_df.index))

# Save the summary table
summary_df.to_csv(os.path.join(out_folder, 'decadal_runoff_percent_change_summary.csv'))
